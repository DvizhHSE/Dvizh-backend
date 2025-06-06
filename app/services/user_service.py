from bson.errors import InvalidId

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

    hashed_password = pwd_context.hash(user_data.password)
    user_dict = user_data.model_dump(exclude={"id"})  # Исключаем id из входных данных
    user_dict.update({
        "password": hashed_password,
        "role": Role.USER.value,
        "events_attended": 0,
        "events_organized": 0
    })

    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})

    # Преобразуем ObjectId в строку перед возвратом
    created_user["_id"] = str(created_user["_id"])
    return User(**created_user)


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