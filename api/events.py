from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.event_service import create_event, get_events

router = APIRouter()

@router.post("/create")
def create_new_event(title: str, date: str, db: Session = Depends(get_db)):
    return create_event(db, title, date)

@router.get("/")
def list_events(db: Session = Depends(get_db)):
    return get_events(db)