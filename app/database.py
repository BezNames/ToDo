"""Подключение к базе данных через SQLAlchemy (SQLite по умолчанию)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    # SQLite: разрешить доступ из разных потоков (FastAPI работает в пуле)
    **({"connect_args": {"check_same_thread": False}} if _is_sqlite else {"pool_recycle": 3600}),
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
