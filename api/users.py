from fastapi import APIRouter, Depends, HTTPException
from database.schemas import User, UserCreate
from services.user_service import create_user, get_user
from database.database import get_db

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    try:
        return await create_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_email}", response_model=User)
async def get_user_by_email(user_email: str):
    user = await get_user(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user