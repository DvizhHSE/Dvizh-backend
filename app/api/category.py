from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.schemas import Category
from app.services import category_service
from typing import List

router = APIRouter(tags=["Category"])

@router.post("/create_categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(name: str):
    """
    Создает новую категорию.
    """
    try:
        return await category_service.create_category(name)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/categories", response_model=List[Category])
async def get_all_categories():
    """
    Возвращает список всех категорий.
    """
    try:
        return await category_service.get_all_categories()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

