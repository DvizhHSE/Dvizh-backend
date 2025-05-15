from database.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))