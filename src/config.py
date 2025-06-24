from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    MODE: Literal["LOCAL", "TEST", "PROD"]

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int

    S3_BUCKET_NAME: str
    S3_STATIC_BUCKET_NAME: str  # бакет с контетном для тестов
    S3_REGION: str
    S3_DOMAIN: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DB_URL_SYNC(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def S3_URL(self):
        return f"https://s3.{self.S3_REGION}.{self.S3_DOMAIN}"

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def get_settings():
    return Settings()
