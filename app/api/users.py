from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import User, UserCreate
from app.services.user_service import create_user, get_full_info_about_user, add_friend_service, register_user_for_event, authenticate_user, update_user
from app.database.database import get_db
from bson.errors import InvalidId
from fastapi import Query
from app.services import event_service

router = APIRouter(tags=["User"])

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    try:
        return await create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login", response_model=User)
async def login_for_access_token(email,password):
    """
    Авторизует пользователя и возвращает данные пользователя.
    """
    user = await authenticate_user(email,password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.patch("/{user_id}", response_model=User)
async def update_user_endpoint(user_id: str, user_data: dict):
    """
    Обновляет данные пользователя.
    """
    try:
        updated_user = await update_user(user_id, user_data)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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

@router.post("/{event_id}/register/{user_id}")
async def register_user_for_event_(event_id: str, user_id: str):
    try:
        await register_user_for_event(event_id, user_id)
        return {"message": "User registered for event"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/home/{user_id}", response_model=dict)
async def get_homepage_data(user_id: str):
    """
    Возвращает данные для главной страницы пользователя:
    - Любимые мероприятия.
    - Мероприятия, на которые записан пользователь.
    - Мероприятия сегодня.
    - Мероприятия на этой неделе.
    """
    try:    
        favorite_events = await event_service.get_favorite_events(user_id)
        planned_events = await event_service.get_future_events_for_user(user_id)
        today_events = await event_service.get_today_events()
        this_week_events = await event_service.get_this_week_events()

        return {     
            "favorite_events": favorite_events,
            "planned_events": planned_events,
            "today_events": today_events,
            "this_week_events": this_week_events
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{user_id}/events")
async def get_user_events(user_id: str):
    """
    Возвращает список всех мероприятий, в которых участвует пользователь (как участник или организатор).
    """
    try:
        return await event_service.get_events_for_user(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/{user_id}/favorites/{event_id}")
async def add_to_favorites(user_id: str, event_id: str):
    """
    Добавляет мероприятие в список любимых пользователя.
    """
    try:
        await event_service.add_event_to_favorites(user_id, event_id)
        return {"message": "Event added to favorites"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/{user_id}/profile-picture")
async def update_user_profile_picture(user_id: str, picture_url: str):
    """
    Обновляет URL картинки профиля пользователя.
    """
    db = await get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"profile_picture": picture_url}}
    )
    return {"message": "Фото обновлено"}


