from sqlalchemy.orm import Session
from database import models
from passlib.context import CryptContext
from fastapi import HTTPException, status


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, email: str, password: str, name: str):
    if get_user(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    hashed = pwd_context.hash(password)
    user = models.User(email=email, password=hashed, name=name)
    db.add(user)
    db.commit()
    return {"id": user.id, "email": user.email, "name": user.name, "password": user.password}

def get_user(db: Session, user_email: str):
    return db.query(models.User).filter(models.User.email == user_email).first()