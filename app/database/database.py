from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from pymongo import IndexModel, ASCENDING
from pymongo.errors import CollectionInvalid
import asyncio
import logging

logger = logging.getLogger(__name__)
client = None
db = None

async def connect_to_mongo():
    global client, db
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to MongoDB (attempt {attempt+1}/{max_retries})")
            client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = client[settings.DB_NAME]
            
            # Проверка соединения
            await db.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            return
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Failed to connect to MongoDB after several attempts")
                raise ConnectionError("Failed to connect to MongoDB")

async def close_mongo_connection():
    if client:
        client.close()
        logger.info("MongoDB connection closed")

async def get_db():
    return db