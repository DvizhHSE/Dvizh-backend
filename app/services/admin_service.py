from app.database.database import get_db
from bson import ObjectId
from fastapi import HTTPException, status
from app.schemas.schemas import User, Event, Achievement

async def deactivate_user(user_id: str):
    db = await get_db()
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )
    return result.modified_count > 0

async def activate_user(user_id: str):
    db = await get_db()
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True}}
    )
    return result.modified_count > 0

async def get_users_with_filters(
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: int = -1,
    search: str = None,
    user_type: str = None,
    is_active: bool = None
):
    db = await get_db()
    skip = (page - 1) * limit
    query = {}
    
    if search:
        query["$or"] = [
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if user_type:
        query["user_type"] = user_type
    
    if is_active is not None:
        query["is_active"] = is_active
    
    users = await db.users.find(query).sort(sort_by, sort_order).skip(skip).limit(limit).to_list(limit)
    
    # Преобразование ObjectId в строки
    for user in users:
        user["_id"] = str(user["_id"])
        user["achievements"] = [str(a) for a in user.get("achievements", [])]
        user["favorite_events"] = [str(e) for e in user.get("favorite_events", [])]
        user["friends"] = [str(f) for f in user.get("friends", [])]
    
    total = await db.users.count_documents(query)
    return {
        "users": users,
        "total": total,
        "page": page,
        "limit": limit
    }