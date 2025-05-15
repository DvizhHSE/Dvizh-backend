from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.user_service import create_user, get_user

router = APIRouter()

@router.post("/register")
def register(email: str, password: str, name: str, db: Session = Depends(get_db)):
    return create_user(db, email, password, name)

@router.get("/{user_email}")
def get_user_by_id(user_email: str, db: Session = Depends(get_db)):
    return get_user(db, user_email)