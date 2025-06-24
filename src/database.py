from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.config import settings

engine = create_async_engine(settings.DB_URL)
engine_null_pool = create_async_engine(settings.DB_URL, poolclass=NullPool)
sync_engine = create_engine(settings.DB_URL_SYNC)
sync_engine_null_pool = create_engine(settings.DB_URL_SYNC, poolclass=NullPool)


async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null_pool = async_sessionmaker(
    bind=engine_null_pool, expire_on_commit=False
)
# для Celery
session_maker = sessionmaker(bind=sync_engine, expire_on_commit=False)
session_maker_null_pool = sessionmaker(bind=sync_engine_null_pool, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
