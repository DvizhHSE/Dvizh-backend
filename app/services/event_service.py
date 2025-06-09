from app.schemas.schemas import Event, EventCreate, Status, User, Category
from app.database.database import get_db
from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.schemas.schemas import Event

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

async def get_events_for_user(user_id: str):
    """
    Возвращает список всех мероприятий, в которых участвует пользователь (как участник или организатор).
    """
    db = await get_db()
    user_oid = ObjectId(user_id)

    # Find events where user is a participant
    participant_events = await db.events.find({"participants": user_oid}).to_list(length=None)

    # Find events where user is an organizer
    organizer_events = await db.events.find({"organizers": user_oid}).to_list(length=None)

    # Combine events and remove duplicates (if any)
    all_events = participant_events + organizer_events
    unique_event_ids = []
    unique_events = []
    for event in all_events:
        if str(event["_id"]) not in unique_event_ids:
            unique_event_ids.append(str(event["_id"]))
            event["_id"] = str(event["_id"])

            # Преобразуем organizers и participants в списки строк
            event["organizers"] = [str(org_id) if isinstance(org_id, ObjectId) else org_id for org_id in event.get("organizers", [])]
            event["participants"] = [str(part_id) if isinstance(part_id, ObjectId) else part_id for part_id in event.get("participants", [])]
            unique_events.append(Event(**event)) # Convert dict to Event model

    return unique_events


async def get_favorite_events(user_id: str):
    """
    Возвращает список любимых мероприятий пользователя.
    """
    db = await get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    favorite_event_ids = user.get("favorite_events", [])
    favorite_events = []
    for event_id in favorite_event_ids:
        event = await db.events.find_one({"_id": ObjectId(event_id)})
        if event:
            event["_id"] = str(event["_id"])
            # Преобразуем organizers и participants в списки строк
            event["organizers"] = [str(org_id) if isinstance(org_id, ObjectId) else org_id for org_id in event.get("organizers", [])]
            event["participants"] = [str(part_id) if isinstance(part_id, ObjectId) else part_id for part_id in event.get("participants", [])]
            favorite_events.append(Event(**event))  # Convert dict to Event model
    return favorite_events


async def get_planned_events_for_user(user_id: str):
    """
    Возвращает список мероприятий со статусом "planned", на которые записан пользователь.
    """
    db = await get_db()
    user_oid = ObjectId(user_id)
    events = await db.events.find({
        "status": "planned",
        "participants": user_oid
    }).to_list(length=None)

    formatted_events = []
    for event in events:
        event["_id"] = str(event["_id"])
        # Преобразуем organizers и participants в списки строк
        event["organizers"] = [str(org_id) if isinstance(org_id, ObjectId) else org_id for org_id in event.get("organizers", [])]
        event["participants"] = [str(part_id) if isinstance(part_id, ObjectId) else part_id for part_id in event.get("participants", [])]
        formatted_events.append(Event(**event))  # Convert dict to Event model
    return formatted_events


async def get_today_events():
    """
    Возвращает список мероприятий, запланированных на сегодня.
    """
    db = await get_db()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    events = await db.events.find({
        "date": {"$gte": today, "$lt": tomorrow}
    }).to_list(length=None)

    formatted_events = []
    for event in events:
        event["_id"] = str(event["_id"])
        # Преобразуем organizers и participants в списки строк
        event["organizers"] = [str(org_id) if isinstance(org_id, ObjectId) else org_id for org_id in event.get("organizers", [])]
        event["participants"] = [str(part_id) if isinstance(part_id, ObjectId) else part_id for part_id in event.get("participants", [])]
        formatted_events.append(Event(**event))  # Convert dict to Event model
    return formatted_events


async def get_this_week_events():
    """
    Возвращает список мероприятий, запланированных на этой неделе (с понедельника по воскресенье).
    """
    db = await get_db()
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=7)  # Next Monday

    events = await db.events.find({
        "date": {"$gte": start_of_week, "$lt": end_of_week}
    }).to_list(length=None)

    formatted_events = []
    for event in events:
        event["_id"] = str(event["_id"])
        # Преобразуем organizers и participants в списки строк
        event["organizers"] = [str(org_id) if isinstance(org_id, ObjectId) else org_id for org_id in event.get("organizers", [])]
        event["participants"] = [str(part_id) if isinstance(part_id, ObjectId) else part_id for part_id in event.get("participants", [])]
        formatted_events.append(Event(**event))  # Convert dict to Event model
    return formatted_events

async def add_event_to_favorites(user_id: str, event_id: str):
    """
    Добавляет мероприятие в список любимых пользователя.
    """
    db = await get_db()

    # Проверяем, существует ли пользователь
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, существует ли мероприятие
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Добавляем мероприятие в список favorite_events пользователя
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"favorite_events": ObjectId(event_id)}}
    )
    return True