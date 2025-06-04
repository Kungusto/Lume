import json
from dotenv import load_dotenv
import os

os.environ["MODE"] = "TEST"
load_dotenv(".env-test", override=True)

import pytest
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.schemas.users import UserAdd
from src.api.dependencies import get_db
from src.database import async_session_maker_null_pool, engine_null_pool, Base
from src.utils.dbmanager import DBManager
from src.config import settings, Settings
from src.main import app

settings = Settings()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with DBManager(session_factory=async_session_maker_null_pool) as _db:
        with open("tests/mock_users.json", "r", encoding="utf-8") as file:
            data = [UserAdd(**user) for user in json.load(file)]
            await _db.users.add_bulk(data)
        await _db.commit()  

async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db

@pytest.fixture(scope="function")
async def db() :
    async for db in get_db_null_pool() :
        yield db

app.dependency_overrides[get_db] = get_db_null_pool

@pytest.fixture(scope="session")
async def ac() :
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
        
@pytest.fixture(scope="session")
async def register_user(ac) :
    response = await ac.post(
       url="/auth/register",
       json={
            "role": "USER",
            "email": "user@user.com",
            "name": "string",
            "surname": "string",
            "nickname": "user1",
            "password": "string"
       } 
    ) 
    assert response.status_code == 200
        

@pytest.fixture(scope="session")
async def auth_ac_user(ac, register_user) :
    response = await ac.post(
        url="/auth/login", json={
            "email": "user@user.com",
            "password": "string"
        }
    )
    assert response.status_code == 200
    assert ac.cookies
    yield ac

@pytest.fixture(scope="session")
async def register_author(ac) :
    response = await ac.post(
        url="/auth/register",
            json={
                "role": "AUTHOR",
                "email": "author@author.com",
                "name": "string",
                "surname": "string",
                "nickname": "author",
                "password": "string"
            }
    ) 
    assert response.status_code == 200


@pytest.fixture(scope="session")
async def auth_ac_author(ac, register_author) :
    response = await ac.post(
        url="/auth/login", json={
            "email": "author@author.com",
            "password": "string"
        }
    )
    assert response.status_code == 200
    assert ac.cookies
    yield ac
