from app.database.database import get_db
from bson import ObjectId
from fastapi import HTTPException, status
from app.schemas.schemas import Category

async def get_category_by_id(category_id: str) -> str:
    db = await get_db()
    category = await db.categories.find_one({"_id": ObjectId(category_id)})
    return category["name"] if category else 'Нет'


async def get_all_categories():
    """
    Возвращает список всех категорий.
    """
    db = await get_db()
    categories = await db.categories.find().to_list(length=None)
    formatted_categories = []
    for category in categories:
        category["_id"] = str(category["_id"])
        formatted_categories.append(Category(**category))
    return formatted_categories

async def create_category(name: str):
    """
    Создает новую категорию.
    """
    db = await get_db()
    category = {"name": name}
    result = await db.categories.insert_one(category)
    created_category = await db.categories.find_one({"_id": result.inserted_id})
    created_category["_id"] = str(created_category["_id"])
    return Category(**created_category)

async def get_all_categories():
    """
    Возвращает список всех категорий.
    """
    db = await get_db()
    categories = await db.categories.find().to_list(length=None)
    formatted_categories = []
    for category in categories:
        category["_id"] = str(category["_id"])
        formatted_categories.append(Category(**category))
    return formatted_categories