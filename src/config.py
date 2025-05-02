from pydantic_settings import BaseSettings

class Settings(BaseSettings): 
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    S3_BUCKET_NAME: str
    S3_REGION: str
    S3_DOMAIN: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def S3_URL(self):
        return f"https://{self.S3_BUCKET_NAME}.s3.{self.S3_REGION}.{self.S3_DOMAIN}"

    class Config:
        env_file = ".env"
        
settings = Settings()