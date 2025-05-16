from database.database import get_db
from database.schemas import Achievement
from bson import ObjectId

async def create_achievement(name: str, picture_url: str):
    db = await get_db()
    achievement = {"name": name, "picture_url": picture_url}
    result = await db.achievements.insert_one(achievement)
    return str(result.inserted_id)

async def grant_achievement(user_id: str, achievement_id: str):
    db = await get_db()
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"achievements": ObjectId(achievement_id)}}
    )