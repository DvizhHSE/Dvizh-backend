from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import Event, EventCreate
from app.services.event_service import create_event, get_all_events,update_event_picture
from app.database.database import get_db

router = APIRouter(tags=["Event"])


@router.post("/{user_id}/create", response_model=Event)
async def create_new_event(event_data: EventCreate, user_id: str):
    try:
        return await create_event(event_data, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{event_id}/event-picture")  # Используем PATCH для обновления
async def update_event_picture_endpoint(event_id: str, event_picture_url: str):
    try:
        await update_event_picture(event_id, event_picture_url)
        return {"message": "Event picture updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/")
async def get_all_events_endpoint():
    try:
        return await get_all_events()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))