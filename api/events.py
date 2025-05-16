from fastapi import APIRouter, Depends, HTTPException
from database.schemas import Event, EventCreate
from services.event_service import create_event
from database.database import get_db

router = APIRouter()


@router.post("/{user_id}/create", response_model=Event)
async def create_new_event(event_data: EventCreate, user_id: str):
    try:
        return await create_event(event_data, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
