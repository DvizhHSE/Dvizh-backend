from fastapi import FastAPI
from app.api import users, events
from app.database.database import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager
from app.database.init_db import init_roles_and_statuses, init_categories
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    try:
        await connect_to_mongo()
        logger.info("Database connection established")
        
        await init_roles_and_statuses()
        logger.info("Roles and statuses initialized")
        
        await init_categories()
        logger.info("Categories initialized")
        
        yield
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise
    finally:
        await close_mongo_connection()
        logger.info("Application shutdown complete")

app = FastAPI(
    lifespan=lifespan,
    title="HSE.Dvizh API",
    description="Backend for event management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(users.router, prefix="/api/users")
app.include_router(events.router, prefix="/api/events")

@app.get("/")
async def root():
    return {"message": "HSE.Dvizh API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected"}