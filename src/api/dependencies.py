from fastapi import Depends
from src.database import async_session_maker
from src.utils.dbmanager import DBManager

async def get_db_manager() : 
    return DBManager(session_factory=async_session_maker)

async def get_db() :
    async with get_db_manager() as db :
        yield db
