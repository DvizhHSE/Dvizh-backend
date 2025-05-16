from fastapi import FastAPI
from api import users, events
from database.database import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)
app.include_router(users.router, prefix="/api/users")
app.include_router(events.router, prefix="/api/events")

@app.get("/")
def read_root():
    return {"message": "HSE.Dvizh API is running"}