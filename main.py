from fastapi import FastAPI
from api import users, events
from database.database import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager
from database.init_db import init_roles_and_statuses, init_categories

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await init_roles_and_statuses()  # Инициализация ролей
    await init_categories()          # Инициализация категорий
    yield
    await close_mongo_connection()



app = FastAPI(lifespan=lifespan)
app.include_router(users.router, prefix="/api/users")
app.include_router(events.router, prefix="/api/events")

@app.get("/")
def read_root():
    return {"message": "HSE.Dvizh API is running"}