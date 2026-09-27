"""Инициализация базы данных: создаёт все таблицы из моделей.

Запуск (один раз, или после изменения моделей):
    python init_db.py

По умолчанию используется SQLite — файл todo.db создастся рядом с проектом.
Для MySQL поменяйте DATABASE_URL в .env и предварительно создайте саму БД
(например, через init_db.sql в MySQL Workbench).
"""
from app import database
from app.database import Base, engine
# ВАЖНО: импортируем модели, чтобы они зарегистрировались в метаданных Base
import app.models.user  # noqa: F401
import app.models.task  # noqa: F401


def init_db() -> None:
    print(f"Подключение к: {settings_url()}")
    Base.metadata.create_all(bind=engine)
    print("Готово: таблицы созданы (существующие таблицы не пересоздаются).")


def settings_url() -> str:
    return database.settings.database_url


if __name__ == "__main__":
    init_db()
