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

class BaseScraper:
    def __init__(self, case_id: int, user_id: int, send_log_func, main_loop):
        self.case_id = case_id
        self.user_id = user_id
        self.send_log_func = send_log_func
        self.main_loop = main_loop
        
        # Load case data
        db = SessionLocal()
        self.case = db.query(Case).get(case_id)
        if self.case:
            self.target_user = self.case.target_username
            self.keywords = self.case.keyword_list
            self.capture_type = self.case.capture_type
            self.max_posts = self.case.max_posts
        db.close()

    def log(self, msg: str):
        db = SessionLocal()
        try:
            case = db.query(Case).get(self.case_id)
            if case:
                case.capture_status_msg = msg
                db.commit()
        finally:
            db.close()
            
        asyncio.run_coroutine_threadsafe(self.send_log_func(self.case_id, msg), self.main_loop)
        print(f"[Scraper Case {self.case_id}] {msg}")

    def log_audit(self, action: str):
        db = SessionLocal()
        try:
            audit = AuditLog(user_id=self.user_id, action=action)
            db.add(audit)
            db.commit()
        finally:
            db.close()

    def update_profile(self, data: dict):
        db = SessionLocal()
        try:
            case = db.query(Case).get(self.case_id)
            if case:
                if data.get('followers'): case.profile_followers = data['followers']
                if data.get('following'): case.profile_following = data['following']
                if data.get('posts'): case.profile_posts = data['posts']
                if data.get('bio'): case.profile_bio = data['bio']
                db.commit()
        finally:
            db.close()

    def save_entry(self, item: dict):
        db = SessionLocal()
        try:
            entry = Entry(
                case_id=self.case_id,
                entry_type=item.get('type', 'post'),
                content=item.get('content', ''),
                author=item.get('author', ''),
                post_timestamp=item.get('timestamp', ''),
                post_url=item.get('url', ''),
                status=item.get('status', 'discovered'),
                likes=str(item.get('likes', '0')),
                reposts=str(item.get('reposts', '0')),
                replies_count=str(item.get('replies', '0')),
                screenshot_path=item.get('screenshot', ''),
                screenshot_hash=item.get('screenshot_hash', '')
            )
            db.add(entry)
            
            case = db.query(Case).get(self.case_id)
            if case:
                case.last_capture = datetime.utcnow()
                
            db.commit()
        except Exception as e:
            print(f"Error saving entry: {e}")
        finally:
            db.close()

    def calculate_sha256(self, filepath: str) -> str:
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return ""

    def keyword_match(self, text: str) -> bool:
        if not self.keywords: return True
        return any(kw.lower() in text.lower() for kw in self.keywords)

class InstagramScraper(BaseScraper):
    
    def extract_profile_stats(self, page):
        stats = {'followers': '?', 'following': '?', 'posts': '?', 'bio': ''}
        
        # Method 1: Try exact DOM elements first (more robust across languages)
        try:
            items = page.query_selector_all('header ul li')
            if len(items) >= 3:
                stats['posts'] = items[0].inner_text().split(' ')[0]
                stats['followers'] = items[1].inner_text().split(' ')[0]
                stats['following'] = items[2].inner_text().split(' ')[0]
        except Exception:
            pass
            
        # Method 2: Fallback to Meta Tag
        if stats['followers'] == '?':
            try:
                meta = page.query_selector('meta[name="description"]')
                if meta:
                    content = meta.get_attribute('content')
                    # Flexible regex to catch localized strings
                    m_f = re.search(r'([\d,\.]+[KkMm]?)\s*Follow', content, re.I)
                    if m_f: stats['followers'] = m_f.group(1)
            except Exception:
                pass
                
        self.update_profile(stats)
        self.log(f"Profile updated: {stats['followers']} followers.")

    def run(self, pw):
        if not self.case:
            return
            
        self.log(f"Starting {self.capture_type} capture for @{self.target_user} (Max: {self.max_posts})...")
        self.log_audit(f"Started capture for Case {self.case_id} (@{self.target_user})")

        try:
            browser = pw.chromium.launch(channel="chrome", headless=False, args=['--start-maximized'])
        except Exception:
            try:
                browser = pw.chromium.launch(channel="msedge", headless=False, args=['--start-maximized'])
            except Exception as e:
                self.log(f"Failed to launch browser: {e}")
                return

        context = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = context.new_page()

        self.log("Navigating to Instagram login...")
        try:
            page.goto("https://www.instagram.com/", timeout=30000)
            page.wait_for_selector('input[name="username"]', timeout=5000)
        except PWTimeout:
            self.log("Waiting for manual login. Please log in to Instagram...")

        # Wait up to 2 mins for user to log in manually
        logged_in = False
        for _ in range(60):
            try:
                if page.query_selector('svg[aria-label="Home"], svg[aria-label="Search"]'):
                    logged_in = True
                    break
            except: pass
            time.sleep(2)
        
        if not logged_in:
            self.log("Login timed out. Aborting capture.")
            browser.close()
            return
            
        self.log("Login confirmed. Navigating to profile...")
        profile_url = f"https://www.instagram.com/{self.target_user}/"
        try:
            page.goto(profile_url, timeout=30000)
            # Wait for the main profile header to load rather than static sleep
            page.wait_for_selector('header', timeout=10000)
        except Exception as e:
            self.log(f"Navigation interrupted or slow: {e}. Proceeding...")

        self.extract_profile_stats(page)

        self.log("Scrolling to find posts...")
        post_links = []
        for i in range(5):
            for link in page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]'):
                href = link.get_attribute('href')
                if href and href not in post_links:
                    post_links.append(href)
            if len(post_links) >= self.max_posts:
                break
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.log(f"Scroll {i+1}/5 - Found {len(post_links)} links")
            time.sleep(1.5)
            
        self.log(f"Extracting URLs for up to {self.max_posts} posts (Discovery Phase)...")
        captured = 0
        for i, href in enumerate(post_links[:self.max_posts]):
            url = f"https://www.instagram.com{href}"
            
            # Extract basic text from grid thumbnail without navigating
            el = page.query_selector(f'a[href="{href}"] img')
            text = el.get_attribute('alt') if el else ""
            
            # Optionally check keywords right away
            if self.keywords and not self.keyword_match(text):
                continue
                
            item = {
                'type': 'post', 'content': text, 'author': self.target_user,
                'url': url, 'status': 'discovered'
            }
            self.save_entry(item)
            captured += 1
            
        self.log(f"Discovery completed! {captured} posts found and indexed.")
        self.log_audit(f"Completed discovery for Case {self.case_id}. Indexed {captured} entries.")
        browser.close()

    def run_targeted(self, pw, entry_id: int):
        db = SessionLocal()
        entry = db.query(Entry).get(entry_id)
        if not entry:
            db.close()
            return
        url = entry.post_url
        db.close()
        
        self.log(f"Starting Targeted Deep Capture for Entry {entry_id}...")
        
        try:
            browser = pw.chromium.launch(channel="chrome", headless=False, args=['--start-maximized'])
        except Exception:
            try:
                browser = pw.chromium.launch(channel="msedge", headless=False, args=['--start-maximized'])
            except Exception as e:
                self.log(f"Failed to launch browser: {e}")
                return
                
        context = browser.new_context(viewport={'width': 1280, 'height': 900})
        page = context.new_page()

        self.log("Navigating to target URL...")
        try:
            page.goto(url, timeout=30000)
            page.wait_for_selector('article', timeout=10000)
        except Exception as e:
            self.log(f"Capture failed or page slow: {e}. Skipping deep extract.")
            browser.close()
            return

        text = entry.content
        for sel in ['article span', 'h1', 'div[data-testid="post-comment-root"] span']:
            el = page.query_selector(sel)
            if el:
                t = el.inner_text()
                if len(t) > len(text): text = t

        likes_count = "0"
        comments_count = "0"
        try:
            likes_el = page.query_selector('a[href$="/liked_by/"] span, section span:has-text("likes")')
            if likes_el:
                l_txt = likes_el.inner_text().strip()
                if "others" in l_txt.lower() or not any(char.isdigit() for char in l_txt):
                    likes_count = "Hidden"
                else:
                    m = re.search(r'([\d,]+)', l_txt)
                    if m: likes_count = m.group(1).replace(',', '')
        except: pass

        fname = f"case{self.case_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{entry_id}.png"
        fpath = str(SCREENSHOT_DIR / fname)
        page.screenshot(path=fpath)
        file_hash = self.calculate_sha256(fpath)

        # Update entry in DB
        db = SessionLocal()
        e = db.query(Entry).get(entry_id)
        if e:
            e.status = 'captured'
            e.content = text
            e.likes = likes_count
            e.replies_count = comments_count
            e.screenshot_path = fname
            e.screenshot_hash = file_hash
            db.commit()
        db.close()
        
        self.log(f"Targeted capture completed for Entry {entry_id}.")
        self.log_audit(f"Performed targeted capture on Entry {entry_id} (Case {self.case_id}).")
        browser.close()

# â”€â”€ Main Capture Flow Wrapper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def capture_flow_sync(case_id: int, user_id: int, send_log_func, main_loop, entry_id: int = None):
    with sync_playwright() as pw:
        scraper = InstagramScraper(case_id, user_id, send_log_func, main_loop)
        if entry_id:
            scraper.run_targeted(pw, entry_id)
        else:
            scraper.run(pw)

async def capture_flow(case_id: int, user_id: int, send_log_func, entry_id: int = None):
    loop = asyncio.get_running_loop()
    await asyncio.to_thread(capture_flow_sync, case_id, user_id, send_log_func, loop, entry_id)
