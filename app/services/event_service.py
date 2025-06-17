from app.schemas.schemas import Event, EventCreate, Status, User, Category
from app.database.database import get_db
from bson import ObjectId
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.schemas.schemas import Event
from app.services.category_service import get_category_by_id


async def create_event(event_data: EventCreate, organizer_id: str):
    db = await get_db()
    event_dict = event_data.model_dump() 

    event_dict.update({
        "organizers": organizer_id,  
        "status": Status.PLANNED.value
    })

    result = await db.events.insert_one(event_dict)

    await db.users.update_one(
        {"_id": organizer_id},  
        {"$inc": {"events_organized": 1}}
    )

    return await get_full_info_about_event(str(result.inserted_id))


async def get_full_info_about_event(event_id: str) -> Event:
    db = await get_db()

    # Получаем событие из базы
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    try:
        validated_event = await validate_event(event)
        event_dict = validated_event.model_dump() 
        event_dict.update({
            "organizers": await get_user_info_string(event_dict["organizers"]),  
    })
        return(event_dict)
    except HTTPException as e:
        print(f"Skipping event {event.get('_id')}: {e.detail}") # Логируем факт пропуска события


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

    # Find events where user is a participant
    participant_events = await db.events.find({"participants": ObjectId(user_id)}).to_list(length=None)

    # Find events where user is an organizer
    organizer_events = await db.events.find({"organizers": user_id}).to_list(length=None)

    # Combine events and remove duplicates (if any)
    all_events = participant_events + organizer_events
    unique_event_ids = []
    unique_events = []
    for event in all_events:
        if str(event["_id"]) not in unique_event_ids:
            unique_event_ids.append(str(event["_id"]))
            try:
                validated_event = await validate_event(event)
                unique_events.append(validated_event)
            except HTTPException as e:
                print(f"Skipping event {event.get('_id')}: {e.detail}") # Логируем факт пропуска события
                continue #Пропускаем событие
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
            try:
                validated_event = await validate_event(event)
                favorite_events.append(validated_event)
            except HTTPException as e:
                print(f"Skipping event {event.get('_id')}: {e.detail}") # Логируем факт пропуска события
                continue #Пропускаем событие
    return favorite_events


async def get_future_events_for_user(user_id: str):
    """
    Возвращает список всех будущих мероприятий, в которых пользователь является
    участником или организатором.  Будущие мероприятия - это мероприятия,
    дата которых больше текущей даты.
    """
    db = await get_db()
    now = datetime.utcnow()  

    events = await db.events.find({
        "$or": [
            {"participants": ObjectId(user_id)},
            {"organizers": user_id}
        ],
        "date": {"$gte": now} 
    }).to_list(length=None)

    formatted_events =[]
    for event in events:
        try:
            validated_event = await validate_event(event)
            formatted_events.append(validated_event)
        except HTTPException as e:
            print(f"Skipping event {event.get('_id')}: {e.detail}")  # Логируем
            continue
        except Exception as e:
            print(f"Skipping event {event.get('_id')}: {e}")  # Логируем
            continue
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
        try:
            validated_event = await validate_event(event)
            formatted_events.append(validated_event)
        except HTTPException as e:
            print(f"Skipping event {event.get('_id')}: {e.detail}") # Логируем факт пропуска события
            continue #Пропускаем событие
        except Exception as e:
             print(f"Skipping event {event.get('_id')}: {e}") # Логируем факт пропуска события
             continue
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
        try:
            validated_event = await validate_event(event)
            formatted_events.append(validated_event)
        except HTTPException as e:
            print(f"Skipping event {event.get('_id')}: {e.detail}") # Логируем факт пропуска события
            continue #Пропускаем событие
        except Exception as e:
             print(f"Skipping event {event.get('_id')}: {e}") # Логируем факт пропуска события
             continue
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

async def update_event_picture(event_id: str, event_picture_url: str):
    """
    Обновляет URL картинки мероприятия.
    """
    db = await get_db()
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    new_photos=event["photos"]
    new_photos[0]=event_picture_url
    result = await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": {"photos": new_photos}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"_id":event_id, "photos": new_photos}
    
async def get_all_events():
    """
    Возвращает список всех мероприятий.
    """
    db = await get_db()
    events = await db.events.find().to_list(length=None)
    formatted_events = []
    for event in events:
        try:
            validated_event = await validate_event(event)
            formatted_events.append(validated_event)
        except HTTPException as e:
            print(f"Skipping event {event.get('_id')}: {e.detail}") # Логируем факт пропуска события
            continue #Пропускаем событие
        except Exception as e:
             print(f"Skipping event {event.get('_id')}: {e}") # Логируем факт пропуска события
             continue
    return formatted_events



async def validate_event(event: dict) -> Event:
    """
    Проверяет валидность события и форматирует его.
    Выбрасывает HTTPException, если событие не валидно.
    """

    event["_id"] = str(event["_id"])

    # Преобразуем organizers и participants в списки строк
    event["participants"] = [str(part_id) if isinstance(part_id, ObjectId) else part_id for part_id in event.get("participants", [])]

    # Получаем категорию
    category = await get_category_by_id(event.get("category_id"))
    org=event.get("organizers")
    if (len(str(org[0]))>1):
        event["organizers"]=str(org[0])
    event["category_id"] = category
    event["photos"] = event.get("photos", [])
    event["description"] = event.get("description", "")
    event["age_limit"] = event.get("age_limit", "0+")
    event["for_roles"] = event.get("for_roles", [])
    print(event)
    return Event(**event)

async def get_user_info_string(user_id: str) -> str:
    """
    "Имя Фамилия, email, телефон (если есть)".
    """
    db = await get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    name = user.get("name", "")  # Получаем имя, подстраховываясь от отсутствия
    surname = user.get("surname", "")  # Получаем фамилию
    email = user.get("email", "")  # Получаем email
    phone_number = user.get("phone_number", "")  # Получаем номер телефона, если есть

    user_info = f"{name} {surname}, {email}"  # Формируем основную часть строки

    if phone_number:
        user_info += f" {phone_number}"  # Добавляем телефон, если он есть

    return user_info