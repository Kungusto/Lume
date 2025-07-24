from src.utils.dbmanager import AsyncDBManager
from src.database import async_session_maker
from contextlib import asynccontextmanager

def get_db_manager():
    return AsyncDBManager(session_factory=async_session_maker)

@asynccontextmanager
async def get_db_as_context_manager():
    async with get_db_manager() as db:
        yield db