from app.database.database import get_db
from app.schemas.schemas import Achievement
from bson import ObjectId
from fastapi import HTTPException

async def create_achievement(name: str, picture_url: str):
    db = await get_db()
    achievement = {"name": name, "picture_url": picture_url}
    result = await db.achievements.insert_one(achievement)
    return str(result.inserted_id)

async def grant_achievement(user_id: str, achievement_id: str):
    db = await get_db()

    # Проверяем, существует ли пользователь
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, существует ли достижение
    achievement = await db.achievements.find_one({"_id": ObjectId(achievement_id)})
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")

    update_result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"achievements": ObjectId(achievement_id)}}
    )

    if update_result.modified_count == 0:
        print("Achievement already granted to user (or no user/achievement found)")
    return True