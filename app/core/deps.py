"""Зависимость аутентификации: извлечение текущего пользователя из JWT."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Недействительный или просроченный токен",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Вернуть пользователя по токену из заголовка Authorization: Bearer <token>."""
    if credentials is None:
        raise CREDENTIALS_ERROR
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise CREDENTIALS_ERROR
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise CREDENTIALS_ERROR
    return user
