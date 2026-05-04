import asyncio
import re
from datetime import datetime
import hashlib
import os
from pathlib import Path
import time
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from database import SessionLocal, Case, Entry, AuditLog

SCREENSHOT_DIR = Path(os.path.join(os.path.dirname(__file__), 'screenshots'))
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def calculate_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def sync_save_entry(case_id: int, item: dict):
    db = SessionLocal()
    try:
        entry = Entry(
            case_id=case_id,
            entry_type=item.get('type', 'post'),
            content=item.get('content', ''),
            author=item.get('author', ''),
            post_timestamp=item.get('timestamp', ''),
            post_url=item.get('url', ''),
            likes=item.get('likes', 0),
            reposts=item.get('reposts', 0),
            replies_count=item.get('replies', 0),
            screenshot_path=item.get('screenshot', ''),
            screenshot_hash=item.get('screenshot_hash', '')
        )
        db.add(entry)
        
        case = db.query(Case).get(case_id)
        if case:
            case.last_capture = datetime.utcnow()
            
        db.commit()
    except Exception as e:
        print(f"Error saving entry: {e}")
    finally:
        db.close()

def sync_update_profile(case_id: int, data: dict):
    db = SessionLocal()
    try:
        case = db.query(Case).get(case_id)
        if case:
            case.profile_followers = data.get('followers', '')
            case.profile_following = data.get('following', '')
            case.profile_posts = data.get('posts', '')
            case.profile_bio = data.get('bio', '')
            db.commit()
    finally:
        db.close()

def sync_log_audit(user_id: int, action: str):
    db = SessionLocal()
    try:
        audit = AuditLog(user_id=user_id, action=action)
        db.add(audit)
        db.commit()
    finally:
        db.close()

def sync_set_case_status(case_id: int, status_msg: str):
    db = SessionLocal()
    try:
        case = db.query(Case).get(case_id)
        if case:
            case.capture_status_msg = status_msg
            db.commit()
    finally:
        db.close()

# ── Main Capture Flow (Synchronous) ──────────────────────────────────────────

def capture_flow_sync(case_id: int, user_id: int, send_log_func, main_loop):
    def log(msg: str):
        # Update db synchronously
        sync_set_case_status(case_id, msg)
        # Send to WebSocket securely from this background thread
        asyncio.run_coroutine_threadsafe(send_log_func(case_id, msg), main_loop)
        print(f"[Scraper Case {case_id}] {msg}")

    db = SessionLocal()
    case = db.query(Case).get(case_id)
    if not case:
        db.close()
        return
    
    target_user = case.target_username
    keywords = case.keyword_list
    capture_type = case.capture_type
    max_posts = case.max_posts
    db.close()

    log(f"Starting {capture_type} capture for @{target_user} (Max: {max_posts})...")
    sync_log_audit(user_id, f"Started capture for Case {case_id} (@{target_user})")

    def keyword_match(text: str) -> bool:
        if not keywords: return True
        return any(kw.lower() in text.lower() for kw in keywords)

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome", headless=False, args=['--start-maximized'])
        except Exception:
            try:
                browser = pw.chromium.launch(channel="msedge", headless=False, args=['--start-maximized'])
            except Exception as e:
                log(f"Failed to launch browser: {e}. Try installing Chrome or run playwright install.")
                sync_log_audit(user_id, f"Case {case_id} capture failed (Browser launch error)")
                return

        context = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = context.new_page()

        log("Navigating to Instagram login...")
        try:
            page.goto("https://www.instagram.com/", timeout=30000)
        except PWTimeout:
            log("Instagram took too long to load.")
            browser.close()
            return

        is_logged_in = False
        try:
            page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
            is_logged_in = True
        except:
            pass

        if not is_logged_in:
            log("Waiting for manual login. Please log in to Instagram in the browser window...")
            logged_in = False
            for _ in range(60):
                try:
                    if page.query_selector('svg[aria-label="Home"]'):
                        logged_in = True
                        break
                except: pass
                time.sleep(2)
            
            if not logged_in:
                log("Login timed out after 2 minutes. Aborting capture.")
                browser.close()
                return
        
        log("Login confirmed. Navigating to profile...")
        profile_url = f"https://www.instagram.com/{target_user}/"
        try:
            page.goto(profile_url, timeout=30000)
            time.sleep(3)
        except Exception as e:
            log(f"Navigation interrupted: {e}. Attempting to continue...")

        try:
            meta = page.query_selector('meta[name="description"]')
            if meta:
                content = meta.get_attribute('content')
                stats = {'followers': '?', 'following': '?', 'posts': '?', 'bio': ''}
                m_f = re.search(r'([\d,\.]+[KkMm]?)\s+Follower', content, re.I)
                if m_f: stats['followers'] = m_f.group(1)
                
                sync_update_profile(case_id, stats)
                log(f"Profile updated: {stats['followers']} followers.")
        except Exception:
            pass

        log("Scrolling to find posts...")
        post_links = []
        for i in range(5):
            for link in page.query_selector_all('a[href*="/p/"]'):
                href = link.get_attribute('href')
                if href and href not in post_links:
                    post_links.append(href)
            if len(post_links) >= max_posts:
                break
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            log(f"Scroll {i+1}/5 - Found {len(post_links)} links")
            time.sleep(1.5)
            
        log(f"Extracting up to {max_posts} posts...")
        captured = 0
        for i, href in enumerate(post_links[:max_posts]):
            url = f"https://www.instagram.com{href}"
            log(f"Processing post {i+1}...")
            try:
                page.goto(url, timeout=20000)
            except Exception as e:
                log(f"Skipping post {i+1} due to navigation error: {e}")
                continue
            time.sleep(2)
            
            text = ""
            for sel in ['article span', 'h1', 'div[data-testid="post-comment-root"] span']:
                el = page.query_selector(sel)
                if el:
                    t = el.inner_text()
                    if len(t) > len(text): text = t

            if not keyword_match(text):
                log(f"Skipping post {i+1}: No keyword match.")
                continue

            # Extract Likes and Comments
            likes_count = 0
            comments_count = 0
            try:
                # Instagram likes are often in 'likes' or 'others' text
                likes_el = page.query_selector('a[href$="/liked_by/"] span, section span:has-text("likes")')
                if likes_el:
                    l_txt = likes_el.inner_text()
                    m = re.search(r'([\d,]+)', l_txt)
                    if m: likes_count = int(m.group(1).replace(',', ''))
            except: pass

            fname = f"case{case_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.png"
            fpath = str(SCREENSHOT_DIR / fname)
            page.screenshot(path=fpath)
            
            file_hash = calculate_sha256(fpath)
            
            item = {
                'type': 'post', 'content': text, 'author': target_user,
                'url': url, 'screenshot': fname, 'screenshot_hash': file_hash,
                'likes': likes_count, 'replies': comments_count
            }
            sync_save_entry(case_id, item)
            captured += 1
            
        log(f"Capture completed! {captured} entries saved.")
        sync_log_audit(user_id, f"Completed capture for Case {case_id}. Found {captured} entries.")
        browser.close()

# The async wrapper that we will call from main.py
async def capture_flow(case_id: int, user_id: int, send_log_func):
    loop = asyncio.get_running_loop()
    await asyncio.to_thread(capture_flow_sync, case_id, user_id, send_log_func, loop)
