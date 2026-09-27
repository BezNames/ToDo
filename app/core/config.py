"""Конфигурация приложения (переменные окружения)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, читаются из переменных окружения / .env."""

    # База данных (MySQL)
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

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()
