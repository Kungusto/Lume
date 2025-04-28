from pydantic_settings import BaseSettings

class Settings: 
    DB_USER: str
    DB_PASSWD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        
settings = Settings()