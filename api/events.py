from fastapi import APIRouter, Depends, HTTPException
from database.schemas import Event, EventCreate
from services.event_service import create_event, get_events
from database.database import get_db

router = APIRouter()

@router.post("/create", response_model=Event)
async def create_new_event(event_data: EventCreate):
    try:
        return await create_event(event_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[Event])
async def list_events():
    return await get_events()