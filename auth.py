import bcrypt
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, User

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

def get_current_active_user(user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def get_current_admin(user: User = Depends(get_current_active_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return user
