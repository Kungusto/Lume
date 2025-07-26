import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """
    Режимы работы:
    - LOCAL: локальная разработка
    - TEST: выполнение тестов
    - PROD: запуск на боевом сервере
    """

    MODE: Literal["LOCAL", "TEST", "PROD"]

    # Базы данных
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # S3 Хранилище
    S3_BUCKET_NAME: str
    S3_STATIC_BUCKET_NAME: str  # бакет с контетном для тестов
    S3_REGION: str
    S3_DOMAIN: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    # Аналитика
    STATEMENT_DIR_PATH: str #  !!! БЕЗ СЛЕША В НАЧАЛЕ !!!

    # Асинхронное подключение
    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Синхронное подключение (только для Celery)
    @property
    def DB_URL_SYNC(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # URL подключения к S3
    @property
    def S3_URL(self):
        return f"https://s3.{self.S3_REGION}.{self.S3_DOMAIN}"

    # URL подключения к Redis
    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def get_settings():
    env_file = os.getenv("ENV_FILE", ".env")
    return Settings(_env_file=env_file)
