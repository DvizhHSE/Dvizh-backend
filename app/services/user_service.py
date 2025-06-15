from bson.errors import InvalidId
from datetime import datetime
from app.schemas.schemas import User, UserCreate, Role, Event, Achievement
from app.database.database import get_db
from passlib.context import CryptContext
from fastapi import HTTPException, status
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(user_data: UserCreate):
    db = await get_db()
    if await db.users.find_one({"email": user_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    #hashed_password = pwd_context.hash(user_data.password)
    user_dict = user_data.model_dump(exclude={"id"})  # Исключаем id из входных данных
    user_dict.update({
        "password": user_data.password,
        "role": Role.USER.value,
        "events_attended": 0,
        "events_organized": 0
    })

    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})

    # Преобразуем ObjectId в строку перед возвратом
    created_user["_id"] = str(created_user["_id"])
    return User(**created_user)

async def authenticate_user(email: str, password: str) -> User:
    """
    Проверяет email и пароль пользователя.
    """
    db = await get_db()
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    #hashed_password =pwd_context.hash(password)
    if (password!=user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    user["_id"] = str(user["_id"])

    return User(**user)

async def get_user_by_id(user_id: str):
    db = await get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    return User(**user) if user else None


async def get_full_info_about_user(user_id: str) -> User:
    db = await get_db()

    # Получаем пользователя из базы
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    # Преобразуем ObjectId в строки для всех полей с ID
    user_data = {
        **user,
        "_id": str(user["_id"]),
        "friends": [str(friend_id) for friend_id in user.get("friends", [])],
        "favorite_events": [str(event_id) for event_id in user.get("favorite_events", [])],
        "achievements": [str(achievement_id) for achievement_id in user.get("achievements", [])]
    }

    # Создаем и возвращаем объект User
    return User(**user_data)


async def add_friend_service(user_oid: ObjectId, friend_oid: ObjectId):
    db = await get_db()

    # Проверяем, что это не попытка добавить самого себя в друзья
    if user_oid == friend_oid:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")

    # Проверяем существование пользователей
    user_exists = await db.users.count_documents({"_id": user_oid}) > 0
    friend_exists = await db.users.count_documents({"_id": friend_oid}) > 0

    if not user_exists or not friend_exists:
        raise HTTPException(status_code=404, detail="User or friend not found")

    # Проверяем, что пользователи еще не друзья
    is_already_friends = await db.users.count_documents({
        "_id": user_oid,
        "friends": friend_oid
    }) > 0

    if is_already_friends:
        raise HTTPException(status_code=400, detail="Users are already friends")

    # Добавляем в друзья (в обе стороны)
    await db.users.update_one(
        {"_id": user_oid},
        {"$addToSet": {"friends": friend_oid}}
    )

    await db.users.update_one(
        {"_id": friend_oid},
        {"$addToSet": {"friends": user_oid}}
    )

    return True

async def register_user_for_event(event_id: str, user_id: str):
    db = await get_db()

    # Verify event exists
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Verify user exists
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is already registered
    if ObjectId(user_id) in [ObjectId(participant) for participant in event.get("participants", [])]:
        raise HTTPException(status_code=400, detail="User already registered for this event")

    # Register user for event
    await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$addToSet": {"participants": ObjectId(user_id)}}
    )

    # Add event to user's attended events (optional, depending on your logic)
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"favorite_events": ObjectId(event_id)}}
    )

    return True
async def update_user_profile_picture(user_id: str, picture_url: str) -> User:
    """
    Обновляет URL картинки профиля пользователя.
    """
    db = await get_db()
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"profile_picture": picture_url}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return User(**user)

async def update_user(user_id: str, user_data: dict) -> User:
    """
    Обновляет данные пользователя.
    """
    db = await get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_data.get("birthday"):
      user_data["birthday"] = datetime.strptime(user_data["birthday"], "%Y-%m-%dT%H:%M:%S")

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    return User(**updated_user)