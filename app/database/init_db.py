from app.database.database import get_db
from app.schemas.schemas import Role, Status
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

async def init_roles_and_statuses():
    db = await get_db()

    if await db.roles.count_documents({}) == 0:
        await db.roles.insert_many([
            {"_id": Role.USER, "name": "Regular User"},
            {"_id": Role.ORGANIZER, "name": "Event Organizer"},
            {"_id": Role.ADMIN, "name": "Administrator"}
        ])
        logger.info("Created initial roles")

    if await db.statuses.count_documents({}) == 0:
        await db.statuses.insert_many([
            {"_id": Status.PLANNED, "name": "Planned"},
            {"_id": Status.ACTIVE, "name": "Active"},
            {"_id": Status.COMPLETED, "name": "Completed"},
            {"_id": Status.CANCELLED, "name": "Cancelled"}
        ])
        logger.info("Created initial statuses")

async def init_categories():
    db = await get_db()
    if await db.categories.count_documents({}) == 0:
        await db.categories.insert_many([
            {"_id": ObjectId(), "name": "Конференция"},
            {"_id": ObjectId(), "name": "Митап"},
            {"_id": ObjectId(), "name": "Хакатон"}
        ])
        logger.info("Created initial categories")