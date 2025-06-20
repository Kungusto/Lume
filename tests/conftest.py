# ruff: noqa: E402

import json
import logging
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
from src.utils.s3_manager import S3Client
from src.constants.files import RequiredFilesForTests

settings = Settings()  # noqa: F811


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
async def db():
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def get_s3client():
    return S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_URL,
        region_name=settings.S3_REGION
    )


@pytest.fixture(scope="session")
async def s3():
    async with get_s3client() as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def check_content(s3):
    files_in_others = await s3.books.list_objects_by_prefix("other/", test=True)
    need_files = RequiredFilesForTests.FILES # файлы, обязательные для тестов, имеющие префикс other/
    missing_files = []
    for need_file in need_files:
        if need_file not in files_in_others:
            missing_files.append(need_file)
    if missing_files:
        logging.warning(
            f"Тесты, связанные с s3-хранилищем пропущены, т.к. отсутствуют обязательтые файлы: {", ".join(missing_files)}"
        )
        return False
    else:
        return True


@pytest.fixture(scope="session", autouse=True)
async def setup_s3(s3):
    assert settings.MODE == "TEST"
    assert settings.S3_BUCKET_NAME.endswith("test")
    file_names = await s3.books.list_objects_by_prefix("")
    await s3.books.delete_bulk(*file_names)


@pytest.fixture(scope="session")
async def register_user(ac):
    response = await ac.post(
        url="/auth/register",
        json={
            "role": "USER",
            "email": "user@user.com",
            "name": "string",
            "surname": "string",
            "nickname": "user1",
            "password": "string",
        },
    )
    assert response.status_code == 200


@pytest.fixture(scope="session")
async def auth_ac_user(ac, register_user):
    response = await ac.post(
        url="/auth/login", json={"email": "user@user.com", "password": "string"}
    )
    assert response.status_code == 200
    assert ac.cookies
    yield ac


@pytest.fixture(scope="session")
async def register_author(ac):
    response = await ac.post(
        url="/auth/register",
        json={
            "role": "AUTHOR",
            "email": "author@author.com",
            "name": "string",
            "surname": "string",
            "nickname": "author",
            "password": "string",
        },
    )
    assert response.status_code == 200


@pytest.fixture(scope="session")
async def auth_ac_author(ac, register_author):
    response = await ac.post(
        url="/auth/login", json={"email": "author@author.com", "password": "string"}
    )
    assert response.status_code == 200
    assert ac.cookies
    yield ac
