"""Подключение к MySQL через SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # переподключаться после простоя MySQL
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""


def get_db():
    """Зависимость FastAPI: сессия БД на время запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
