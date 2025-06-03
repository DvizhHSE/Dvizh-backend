from app.schemas.schemas import Event, EventCreate, Status, User, Category
from app.database.database import get_db
from bson import ObjectId
from fastapi import HTTPException, status


async def create_event(event_data: EventCreate, organizer_id: str):
    db = await get_db()
    event_dict = event_data.model_dump()

    # Конвертируем organizer_id в ObjectId
    organizer_oid = ObjectId(organizer_id)  # Добавьте эту строку

    event_dict.update({
        "organizers": [organizer_oid],  # Используем ObjectId здесь
        "status": Status.PLANNED.value
    })

    result = await db.events.insert_one(event_dict)

    # Обновляем счётчик организатора (ObjectId уже есть)
    await db.users.update_one(
        {"_id": organizer_oid},  # Используем существующий ObjectId
        {"$inc": {"events_organized": 1}}
    )

    # Возвращаем событие с конвертацией ObjectId -> str
    return await get_full_info_about_event(str(result.inserted_id))


async def get_full_info_about_event(event_id: str) -> Event:
    db = await get_db()

    # Получаем событие из базы
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        return None

    # Преобразуем ObjectId в строки для всех полей с ID
    event_data = {
        **event,
        "_id": str(event["_id"]),
        "participants": [str(participant_id) for participant_id in event.get("participants", [])],
        "organizers": [str(organizer_id) for organizer_id in event.get("organizers", [])],
        "category_id": str(event["category_id"]) if "category_id" in event else None
    }

    # Создаем и возвращаем объект Event
    return Event(**event_data)


async def add_participant(event_id: str, user_id: str):
    db = await get_db()
    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$addToSet": {"participants": ObjectId(user_id)}}
    )

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"events_attended": 1}}
    )