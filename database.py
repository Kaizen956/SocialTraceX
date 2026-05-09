from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
import os

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'forensic.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ── USERS ────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="examiner")  # 'admin' or 'examiner'
    name = Column(String(100), default="Examiner")
    created_at = Column(DateTime, default=datetime.utcnow)

# ── CASES ────────────────────────────────────────────────────────────────────
class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    target_username = Column(String(100), nullable=False)
    platform = Column(String(50), nullable=False)
    
    status = Column(String(20), default="active")
    keywords = Column(Text, default="")
    capture_type = Column(String(20), default="posts") # 'posts' or 'messages'
    max_posts = Column(Integer, default=10)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_capture = Column(DateTime, nullable=True)
    capture_status_msg = Column(String(200), default="Ready")
    
    # Profile stats
    profile_followers = Column(Text, default="")
    profile_following = Column(Text, default="")
    profile_posts = Column(Text, default="")
    profile_bio = Column(Text, default="")
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    events = relationship("Event", backref="case", cascade="all, delete-orphan")

    @property
    def keyword_list(self):
        if not self.keywords:
            return []
        return [k.strip() for k in self.keywords.split(",") if k.strip()]

# ── EVENTS ──────────────────────────────────────────────────────────────────
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    
    status = Column(String(20), default="discovered") # 'discovered' or 'captured'
    event_type = Column(String(20), default="dm") # 'dm', 'post'
    
    from_user = Column(String(100), default="")
    to_user = Column(String(100), default="")
    timestamp = Column(String(50), default="")
    length = Column(Integer, default=0)
    contains_media = Column(Boolean, default=False)
    
    # Optional metadata or parsed content
    content = Column(Text, default="")
    profile_pic_url = Column(String(500), default="")
    
    screenshot_path = Column(String(500), default="")
    screenshot_hash = Column(String(64), default="")  # SHA-256 for evidence integrity
    
    include_in_report = Column(Boolean, default=False)
    flagged = Column(Boolean, default=False)
    notes = Column(Text, default="")
    captured_at = Column(DateTime, default=datetime.utcnow)

# ── AUDIT LOG ────────────────────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(200), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
