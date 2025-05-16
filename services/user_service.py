from database.models import User, UserCreate
from database.database import get_db
from passlib.context import CryptContext
from fastapi import HTTPException, status
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(user_data: UserCreate):
    db = await get_db()
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    hashed_password = pwd_context.hash(user_data.password)
    user_dict = user_data.model_dump()
    user_dict["password"] = hashed_password
    user_dict.pop("id", None)

    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    return User(**created_user)


async def get_user(user_email: str):
    db = await get_db()
    user = await db.users.find_one({"email": user_email})
    if user:
        return User(**user)
    return None