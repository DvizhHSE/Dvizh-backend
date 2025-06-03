from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import User, UserCreate
from app.services.user_service import create_user, get_full_info_about_user, add_friend_service
from app.database.database import get_db
from bson.errors import InvalidId
from fastapi import Query

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    try:
        return await create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{user_id}",
    response_model=User,
    responses={
        200: {
            "description": "Успешный ответ",
            "content": {
                "application/json": {
                    "example": {
                        "id": "507f1f77bcf86cd799439011",
                        "password": "237f1f77bcf86cd799439011",
                        "name": "Иван Иванов",
                        "email": "user@example.com",
                        "profile_picture": "https://example.com/pic.jpg",
                        "role": "user",
                        "favorite_events": [{}, {}],
                        "friends": [{}, {}],
                        "achievements": [{}, {}],
                        "events_attended": 3,
                        "events_organized": 2
                    }
                }
            }
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
async def get_user_info(user_id: str):
    user = await get_full_info_about_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/add_friend")  # Лучше использовать POST для таких операций
async def add_friend_endpoint(
        user_id: str = Query(..., description="ID пользователя"),
        friend_id: str = Query(..., description="ID друга")
):
    try:
        # Проверяем валидность ID
        try:
            user_oid = ObjectId(user_id)
            friend_oid = ObjectId(friend_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ID format")

        result = await add_friend_service(user_oid, friend_oid)
        return {"status": "success", "message": "Friend added successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
