"""Безопасность: хэширование паролей с солью и JWT-токены."""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt сам генерирует криптостойкую соль для каждого пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Вернуть bcrypt-хэш пароля (соль встроена в хэш)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль, сверив его с сохранённым хэшем."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str) -> str:
    """Создать JWT-токен доступа."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    """Проверить и декодировать JWT-токен. None, если токен недействителен."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
