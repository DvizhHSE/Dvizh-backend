from app.database.database import get_db
from app.schemas.schemas import Category
from bson import ObjectId

async def create_category(name: str):
    db = await get_db()
    category = {"name": name}
    result = await db.categories.insert_one(category)
    return str(result.inserted_id)

async def get_category_by_id(category_id: str):
    db = await get_db()
    category = await db.categories.find_one({"_id": ObjectId(category_id)})
    return Category(**category) if category else None