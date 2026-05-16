from fastapi import FastAPI, Request, Form, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import asyncio
import os

from database import Base, engine, get_db, User, Case, Event, AuditLog
from auth import verify_password, get_password_hash, get_current_user, get_current_admin, get_current_active_user
from scraper import capture_flow, capture_flow_batch
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init Admin User on startup
    db = next(get_db())
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(username="admin", hashed_password=get_password_hash("admin123"), role="admin", name="Lead Administrator")
        db.add(admin)
        db.commit()
    if not db.query(User).filter(User.username == "examiner").first():
        examiner = User(username="examiner", hashed_password=get_password_hash("forensic123"), role="examiner", name="Field Examiner")
        db.add(examiner)
        db.commit()
    yield

app = FastAPI(title="ForensicView FastAPI", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="super-secret-key-forensic-tool-2024")

# Directories
BASE_DIR = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/screenshots", StaticFiles(directory=os.path.join(BASE_DIR, "screenshots")), name="screenshots")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# WebSocket Manager for Live Logging
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, case_id: int):
        await websocket.accept()
        if case_id not in self.active_connections:
            self.active_connections[case_id] = []
        self.active_connections[case_id].append(websocket)

    def disconnect(self, websocket: WebSocket, case_id: int):
        if case_id in self.active_connections:
            self.active_connections[case_id].remove(websocket)

    async def broadcast_log(self, case_id: int, message: str):
        if case_id in self.active_connections:
            for connection in self.active_connections[case_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# ── ROUTES ───────────────────────────────────────────────────────────────────

@app.get("/")
def read_root(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@app.post("/login")
def login_post(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": "Invalid credentials"})
    
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    active_cases = db.query(Case).filter(Case.status == 'active').count()
    total_entries = db.query(Event).count()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "request": request, "user": user, "cases": cases,
        "active_cases": active_cases, "total_entries": total_entries
    })

@app.post("/cases/new")
def create_case(
    request: Request, 
    title: str = Form(...), target_username: str = Form(...), platform: str = Form(...),
    description: str = Form(""),
    user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    case = Case(
        title=title, target_username=target_username.lstrip('@'), platform=platform,
        description=description, capture_type="posts", max_posts=10,
        created_by=user.id
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return RedirectResponse(url=f"/cases/{case.id}", status_code=303)

@app.get("/cases/{case_id}", response_class=HTMLResponse)
def view_case(request: Request, case_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    entries = db.query(Event).filter(Event.case_id == case_id).order_by(Event.id.desc()).all()
    return templates.TemplateResponse(request=request, name="case_detail.html", context={"request": request, "user": user, "case": case, "entries": entries})

class DiscoveryRequest(BaseModel):
    capture_type: str = None
    max_posts: int = 10

@app.post("/cases/{case_id}/capture")
async def start_capture(case_id: int, request: DiscoveryRequest = None, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if request:
        if request.capture_type:
            case.capture_type = request.capture_type
        if request.max_posts is not None:
            case.max_posts = request.max_posts
        db.commit()

    # Fire Phase A scraper in background
    asyncio.create_task(capture_flow(case_id, user.id, manager.broadcast_log))
    return {"status": "started"}

@app.post("/cases/{case_id}/entries/{entry_id}/capture_targeted")
async def start_targeted_capture(case_id: int, entry_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    entry = db.query(Event).filter(Event.id == entry_id, Event.case_id == case_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Fire Phase B scraper for just this event
    asyncio.create_task(capture_flow(case_id, user.id, manager.broadcast_log, entry_id=entry_id))
    return {"status": "started"}

class BatchCaptureRequest(BaseModel):
    mode: str
    keywords: str = None

@app.post("/cases/{case_id}/capture_batch")
async def start_batch_capture(case_id: int, request: BatchCaptureRequest, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    events = db.query(Event).filter(Event.case_id == case_id, Event.status == 'discovered').all()
    
    target_ids = []
    if request.mode == 'all':
        target_ids = [e.id for e in events]
    elif request.mode == 'keywords':
        kw_list = [k.strip() for k in request.keywords.split(",") if k.strip()] if request.keywords else []
        for e in events:
            if kw_list and e.content:
                if any(kw.lower() in e.content.lower() for kw in kw_list):
                    target_ids.append(e.id)
                    
    if not target_ids:
        return {"status": "no targets found"}
        
    asyncio.create_task(capture_flow_batch(case_id, user.id, manager.broadcast_log, target_ids))
    return {"status": "started", "targets": len(target_ids)}

@app.get("/cases/{case_id}/visual_data")
def get_visual_data(case_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    case = db.query(Case).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    events = db.query(Event).filter(Event.case_id == case_id).all()
    
    # We want to build a graph of Accounts
    # Target user is the center
    target_node_id = f"user_{case.target_username}"
    
    nodes_dict = {
        target_node_id: {
            "id": target_node_id, 
            "label": f"@{case.target_username}", 
            "shape": "image", 
            "image": "https://cdn-icons-png.flaticon.com/512/149/149071.png", 
            "size": 40
        }
    }
    
    edges_dict = {}
    
    user_interaction_volume = {} # For the chart
    
    for e in events:
        # Determine the "other" person
        other_user = e.to_user if e.from_user == case.target_username else e.from_user
        if not other_user: continue
        
        other_node_id = f"user_{other_user}"
        
        if other_node_id not in nodes_dict:
            pic_url = e.profile_pic_url if e.profile_pic_url else "https://cdn-icons-png.flaticon.com/512/149/149071.png"
            nodes_dict[other_node_id] = {
                "id": other_node_id,
                "label": f"@{other_user}",
                "shape": "image",
                "image": pic_url,
                "size": 25,
                # Add event_id to the node data so frontend can trigger capture based on the latest interaction
                "latest_event_id": e.id,
                "status": e.status
            }
        else:
            # Update status if captured
            if e.status == 'captured':
                nodes_dict[other_node_id]["status"] = 'captured'
            # Keep latest event_id
            nodes_dict[other_node_id]["latest_event_id"] = e.id
            
        # Add Edge
        edge_id = f"{target_node_id}-{other_node_id}"
        if edge_id not in edges_dict:
            edges_dict[edge_id] = {"from": target_node_id, "to": other_node_id, "width": 1}
        else:
            edges_dict[edge_id]["width"] += 1 # Thicker edge for more interactions
            
        # Accumulate volume for chart
        if other_user not in user_interaction_volume:
            user_interaction_volume[other_user] = 0
        user_interaction_volume[other_user] += (e.length or 1)
        
    nodes = list(nodes_dict.values())
    
    # Highlight captured nodes with a border if possible, or adjust size
    for n in nodes:
        if n.get("status") == 'captured':
            n["borderWidth"] = 4
            n["color"] = {"border": "#10b981"}
    
    edges = list(edges_dict.values())
    
    # Sort chart data by volume
    sorted_users = sorted(user_interaction_volume.items(), key=lambda x: x[1], reverse=True)[:10]
    chart_labels = [f"@{u[0]}" for u in sorted_users]
    chart_lengths = [u[1] for u in sorted_users]

    return {
        "nodes": nodes,
        "edges": edges,
        "chart_data": {
            "labels": chart_labels,
            "lengths": chart_lengths
        }
    }

@app.post("/cases/{case_id}/entries/{entry_id}/toggle_report")
def toggle_report(case_id: int, entry_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    entry = db.query(Event).filter(Event.id == entry_id, Event.case_id == case_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")
    
    entry.include_in_report = not entry.include_in_report
    db.commit()
    return {"status": "success", "included": entry.include_in_report}

@app.get("/cases/{case_id}/report", response_class=HTMLResponse)
def generate_report(request: Request, case_id: int, user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    included_entries = db.query(Event).filter(Event.case_id == case_id, Event.status == 'captured').order_by(Event.id.desc()).all()
    return templates.TemplateResponse(request=request, name="report.html", context={"request": request, "user": user, "case": case, "entries": included_entries})

@app.websocket("/ws/case/{case_id}/logs")
async def websocket_endpoint(websocket: WebSocket, case_id: int):
    await manager.connect(websocket, case_id)
    try:
        while True:
            # keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, case_id)

# ── ADMIN PANEL ──────────────────────────────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50).all()
    return templates.TemplateResponse(request=request, name="admin.html", context={"request": request, "user": user, "users": users, "logs": logs})

@app.post("/admin/users/new")
def create_user(
    request: Request, username: str = Form(...), password: str = Form(...), role: str = Form(...), name: str = Form(...),
    user: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    new_user = User(username=username, hashed_password=get_password_hash(password), role=role, name=name)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
