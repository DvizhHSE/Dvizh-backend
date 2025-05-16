from database.database import connect_to_mongo, get_db
from database.schemas import Role, Status
from bson import ObjectId


async def init_roles_and_statuses():
    db = await get_db()

    # Инициализация ролей
    if await db.roles.count_documents({}) == 0:
        await db.roles.insert_many([
            {"_id": Role.USER, "name": "Regular User"},
            {"_id": Role.ORGANIZER, "name": "Event Organizer"},
            {"_id": Role.ADMIN, "name": "Administrator"}
        ])

    # Инициализация статусов
    if await db.statuses.count_documents({}) == 0:
        await db.statuses.insert_many([
            {"_id": Status.PLANNED, "name": "Planned"},
            {"_id": Status.ACTIVE, "name": "Active"},
            {"_id": Status.COMPLETED, "name": "Completed"},
            {"_id": Status.CANCELLED, "name": "Cancelled"}
        ])


async def init_categories():
    db = await get_db()
    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many([
            {"_id": ObjectId(), "name": "Конференция"},
            {"_id": ObjectId(), "name": "Митап"},
            {"_id": ObjectId(), "name": "Хакатон"}
        ])