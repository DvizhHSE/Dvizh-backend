from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from pymongo import IndexModel
from pymongo.errors import CollectionInvalid

client = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DB_NAME]

    # Создаем индексы при подключении
    try:
        await db.users.create_indexes([
            IndexModel([("email", 1)], unique=True)
        ])
    except CollectionInvalid:
        pass


async def close_mongo_connection():
    if client:
        client.close()


async def get_db():
    return db