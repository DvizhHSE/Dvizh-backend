from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic_core import core_schema
from enum import Enum


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        def validate(value):
            if isinstance(value, ObjectId):
                return str(value)
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return value

        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return handler(core_schema.str_schema())


class Role(str, Enum):
    USER = "user"
    ORGANIZER = "organizer"
    ADMIN = "admin"


class Category(str, Enum):
    CONFERENCE = "Конференция",
    MEETUP = "Митап",
    HACKATON = "Хакатон"


class Achievement(BaseModel):
    id: PyObjectId = Field(alias="_id")
    achievement_picture: Optional[str] = None
    name: str
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Самый умный",
                "achievement_picture": "https://example.com/pic.jpg"
            }
        }
    )

class Status(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None


class UserCreate(UserBase):
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Иван Иванов",
                "email": "user@example.com",
                "password": "securepassword123",
                "profile_picture": "https://example.com/pic.jpg"
            }
        }
    )


class User(UserBase):
    id: PyObjectId = Field(alias="_id")
    password: str
    favorite_events: List[PyObjectId] = []
    friends: List[PyObjectId] = []
    achievements: List[PyObjectId] = []
    events_attended: int = 0
    events_organized: int = 0
    role: Role = Role.USER

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "password": "237f1f77bcf86cd799439011",
                "name": "Иван Иванов",
                "email": "user@example.com",
                "profile_picture": "https://example.com/pic.jpg",
                "role": "user",
                "favorite_events": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439011"],
                "friends": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439011"],
                "achievements": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439011"],
                "events_attended": 3,
                "events_organized": 2
            }
        }
    )


class EventBase(BaseModel):
    name: str
    date: datetime
    location: str
    category_id: PyObjectId


class EventCreate(EventBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Конференция по Python",
                "date": "2023-12-15T10:00:00",
                "location": "Москва, ул. Пушкина 10",
                "category_id": "507f1f77bcf86cd799439011"
            }
        }
    )


class Event(EventBase):
    id: PyObjectId = Field(alias="_id")
    participants: List[PyObjectId] = []
    organizers: List[PyObjectId] = []
    status: Status = Status.PLANNED

    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "name": "Конференция по Python",
                "date": "2023-12-15T10:00:00",
                "participants": ["307f1f77bcf86cd799439012", "407f1f77bcf86cd799439012"],
                "organizers": ["707f1f77bcf86cd799439012", "507f1f77bcf86cd799439012"],
                "location": "Москва, ул. Пушкина 10",
                "category_id": "507f1f77bcf86cd799439011",
                "status": "planned"
            }
        }
    )