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


def _migrate_sqlite_columns() -> None:
    """Добавляет новые колонки tasks, если БД создана до обновления модели."""
    from sqlalchemy import inspect, text

    if not database.settings.database_url.startswith("sqlite"):
        return
    insp = inspect(engine)
    if "tasks" not in insp.get_table_names():
        return
    existing = {c["name"] for c in insp.get_columns("tasks")}
    to_add = {
        "priority": "VARCHAR(6) NOT NULL DEFAULT 'medium'",
        "due_date": "DATE",
        "duration_minutes": "INTEGER",
    }
    with engine.begin() as conn:
        for col, ddl in to_add.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE tasks ADD COLUMN {col} {ddl}"))
                print(f"Миграция: добавлена колонка tasks.{col}")


def init_db() -> None:
    print(f"Подключение к: {settings_url()}")
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_columns()
    print("Готово: таблицы созданы (существующие таблицы не пересоздаются).")


def settings_url() -> str:
    return database.settings.database_url


if __name__ == "__main__":
    init_db()
