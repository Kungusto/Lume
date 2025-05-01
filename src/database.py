from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings

engine = create_async_engine(settings.DB_URL)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase) :
    pass