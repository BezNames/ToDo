"""Конфигурация приложения (переменные окружения)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, читаются из переменных окружения / .env."""

    # База данных. По умолчанию — локальный файл SQLite (без установки MySQL).
    # Для MySQL раскомментируйте блок ниже в .env и поменяйте DATABASE_URL.
    database_url: str = "sqlite:///./todo.db"

    # Старые переменные MySQL (не используются, пока DATABASE_URL задан явно)
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "todo_user"
    db_password: str = "todo_pass"
    db_name: str = "todo_db"

    # JWT-аутентификация
    secret_key: str = "CHANGE_ME_IN_ENV"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # сутки

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
