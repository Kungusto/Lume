import pytest
import json
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.database import async_session_maker_null_pool, engine_null_pool, Base
from src.utils.dbmanager import DBManager
from src.config import settings, Settings
from src.main import app
from src.schemas.users import UserAdd

from dotenv import load_dotenv
import os

os.environ["MODE"] = "TEST"
load_dotenv(".env-test", override=True)

settings = Settings()

@pytest.fixture(scope="session", autouse=True)
async def setup_database(db):
    assert settings.MODE == "TEST"

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with DBManager(session_factory=async_session_maker_null_pool) as _db:
        with open("tests/mock_hotels.json", "r", encoding="utf-8") as file:
            data = [UserAdd(**user) for user in json.load(file)]
            await _db.hotels.add_bulk(data)
        await _db.commit()

    

async def get_db_null_pull() :
    return DBManager(session_factory=async_session_maker_null_pool)

@pytest.fixture(scope="session")
async def db() :
    async for db in get_db_null_pull() :
        yield db

@pytest.fixture(scope="session")
async def ac() :
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
        
@pytest.fixture(scope="session")
async def auth_ac_user(ac) :
    await ac.post(
        url="/auth/login", json={}
    )
    yield ac


