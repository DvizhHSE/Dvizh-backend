from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from pymongo import IndexModel, ASCENDING
from pymongo.errors import CollectionInvalid

client = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DB_NAME]

    # Создаем индексы
    try:
        await db.users.create_indexes([
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("favorite_events", ASCENDING)]),
            IndexModel([("friends", ASCENDING)])
        ])

        await db.events.create_indexes([
            IndexModel([("date", ASCENDING)]),
            IndexModel([("category_id", ASCENDING)]),
            IndexModel([("participants", ASCENDING)]),
            IndexModel([("organizers", ASCENDING)])
        ])

        await db.categories.create_index([("name", ASCENDING)], unique=True)

    except CollectionInvalid as e:
        print(f"Index creation error: {e}")


async def close_mongo_connection():
    if client:
        client.close()


async def get_db():
    return db