from database.models import Event, EventCreate
from database.database import get_db
from bson import ObjectId


async def create_event(event_data: EventCreate):
    db = await get_db()
    event_dict = event_data.model_dump()
    if event_dict.get("user_id"):
        event_dict["user_id"] = ObjectId(event_dict["user_id"])

    result = await db.events.insert_one(event_dict)
    created_event = await db.events.find_one({"_id": result.inserted_id})
    return Event(**created_event)


async def get_events():
    db = await get_db()
    events = []
    async for event in db.events.find():
        events.append(Event(**event))
    return events