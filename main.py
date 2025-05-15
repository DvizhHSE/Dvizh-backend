from fastapi import FastAPI
from api import users, events
from database.database import engine, Base
from database.models import User, Event

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router, prefix="/api/users")
app.include_router(events.router, prefix="/api/events")

@app.get("/")
def read_root():
    return {"message": "HSE.Dvizh API is running"}