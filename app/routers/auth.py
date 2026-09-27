"""Роутер регистрации и входа."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Зарегистрировать пользователя. Пароль хэшируется bcrypt (соль внутри хэша)."""
    exists = db.query(User).filter(
        or_(User.username == data.username, User.email == data.email)
    ).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином или email уже существует",
        )
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Вход по логину или email. Возвращает JWT-токен."""
    user = (
        db.query(User)
        .filter(or_(User.username == data.username, User.email == data.username))
        .first()
    )
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.id, user.username)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    """Текущий пользователь (по токену)."""
    return current_user
