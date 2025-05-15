from sqlalchemy.orm import Session
from database.models import Event

def create_event(db: Session, title: str, date: str):
    new_event = Event(title=title, date=date)
    db.add(new_event)
    db.commit()
    return {"id": new_event.id, "title": title, "date": date}

def get_events(db: Session):
    return db.query(Event).all()