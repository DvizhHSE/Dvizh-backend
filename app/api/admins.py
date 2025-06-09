from fastapi import APIRouter, Depends, HTTPException
from app.services.admin_service import (
    deactivate_user,
    activate_user,
    get_users_with_filters
)
from app.services.achievement_service import grant_achievement, create_achievement
from app.database.database import get_db
from bson import ObjectId
from fastapi import Query

router = APIRouter(tags=["Admin"])

@router.post("/users/{user_id}/deactivate")
async def deactivate_user_endpoint(user_id: str):
    if not await deactivate_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated"}

@router.post("/users/{user_id}/activate")
async def activate_user_endpoint(user_id: str):
    if not await activate_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated"}

@router.post("/users/{user_id}/grant-achievement/{achievement_id}")
async def grant_achievement_endpoint(user_id: str, achievement_id: str):
    await grant_achievement(user_id, achievement_id)
    return {"message": "Achievement granted"}

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: int = Query(-1),
    search: str = Query(None),
    user_type: str = Query(None),
    is_active: bool = Query(None)
):
    return await get_users_with_filters(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        user_type=user_type,
        is_active=is_active
    )

@router.post("/create_achievement")
async def create_achievement_endpoint(name: str, picture_url: str):
    message= await create_achievement(name, picture_url)
    if not message:
        raise HTTPException(status_code=404, detail="Error")
    return message