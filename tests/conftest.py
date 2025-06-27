# ruff: noqa: E402

import asyncio
import json
import logging
from typing import Generator
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
from src.schemas.books import GenreAdd, BookAddWithAuthorsTagsGenres
from src.services.auth import AuthService
from src.api.dependencies import get_db
from src.database import async_session_maker_null_pool, engine_null_pool, Base
from src.utils.dbmanager import AsyncDBManager
from src.config import settings, Settings
from src.main import app
from src.utils.s3_manager import AsyncS3Client
from src.constants.files import RequiredFilesForTests
from src.connectors.redis_connector import RedisManager
from src.tasks.celery_app import celery_app

settings = Settings()  # noqa: F811


@pytest.fixture(autouse=True)
def setup_celery():
    celery_app.conf.task_always_eager = True
    yield
    celery_app.conf.task_always_eager = False


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create and provide an event loop for async tests."""
    logging.debug("Создание нового цикла событий")
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def redis():
    async with RedisManager(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT
    ) as redis:
        try:
            result = await redis.ping()
        except Exception as e:
            logging.warning(f"Не удалось подключиться к Redis: {e}")
            pytest.skip("Redis не работает — тест пропущен")

        if not result:
            logging.warning("Не удалось получить успешный ping Redis, тест пропущен")
            pytest.skip("Redis ping неудачен — тест пропущен")

        yield redis


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"

    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncDBManager(session_factory=async_session_maker_null_pool) as _db:
        with open("tests/mock_users.json", "r", encoding="utf-8") as file:
            data = []
            for user in json.load(file):
                hashed_password = AuthService().hash_password(user["hashed_password"])
                user["hashed_password"] = hashed_password
                data.append(UserAdd(**user))
            await _db.users.add_bulk(data)
        with open("tests/mock_genres.json", "r", encoding="utf-8") as file:
            data = [GenreAdd(**genre) for genre in json.load(file)]
            await _db.genres.add_bulk(data)
        await _db.commit()


@pytest.fixture(scope="session", autouse=True)
async def mock_books(setup_database, auth_ac_author):
    with open("tests/mock_books.json", "r", encoding="utf-8") as file:
        for book in json.load(file):
            response = await auth_ac_author.post(
                url="/author/book",
                json=BookAddWithAuthorsTagsGenres(**book).model_dump(mode="json"),
            )
            assert response.status_code == 200


@pytest.fixture(scope="session", autouse=True)
async def mock_s3(s3_session, mock_books, auth_ac_author):
    """Добавляем обложку к книге с id=2 для теста на изменение обложки"""
    logging.info("Добавляю обложку к книге id=2")
    assert settings.MODE == "TEST"
    file = await s3_session.books.get_file_by_path(
        is_content_bucket=True, s3_path="books/covers/normal_cover.jpg"
    )
    response_add_cover = await auth_ac_author.post(
        url="author/cover/2", files={"file": ("preview.png", file)}
    )
    assert response_add_cover.status_code == 200


async def get_db_null_pool():
    async with AsyncDBManager(session_factory=async_session_maker_null_pool) as db:
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


@pytest.fixture(scope="session")
async def ac_session():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def get_async_s3client():
    return AsyncS3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_URL,
        region_name=settings.S3_REGION,
    )


@pytest.fixture(scope="session")
async def s3_session():
    async with get_async_s3client() as client:
        yield client


@pytest.fixture(scope="function")
async def s3():
    async with get_async_s3client() as client:
        yield client


@pytest.fixture(scope="session")
async def check_content_unit_tests(s3_session):
    files_in_others = await s3_session.books.list_objects_by_prefix(
        "other/", is_content_bucket=True
    )
    files_with_prefix_to_delete = await s3_session.books.list_objects_by_prefix(
        "files_to_delete/", is_content_bucket=True
    )
    if not files_with_prefix_to_delete:
        logging.warning(
            " не найдены обязательные файлы unit-тестов в S3 \
            \nдолжен быть хотя-бы один файл с префиксом 'files_to_delete/'"
        )
        pytest.skip("Тест пропущен. Отсутствуют обязательные файлы")
    need_files = (
        RequiredFilesForTests.UNIT_TESTS_FILES
    )  # файлы, обязательные для тестов (имеющие префикс other/)
    missing_files = []
    for need_file in need_files:
        if need_file not in files_in_others:
            missing_files.append(need_file)
    if missing_files:
        logging.warning(
            f" не найдены обязательные файлы unit-тестов в S3 — {', '.join(missing_files)}"
        )
        pytest.skip("Тест пропущен. Отсутствуют обязательные файлы")
        return False
    else:
        return True


@pytest.fixture(scope="session")
async def check_content_integration_tests(s3_session):
    files_in_others = await s3_session.books.list_objects_by_prefix(
        "books/", is_content_bucket=True
    )
    need_files = (
        RequiredFilesForTests.INTEGRATION_TESTS_FILES
    )  # файлы, обязательные для тестов (имеющие префикс other/)
    missing_files = []
    for need_file in need_files:
        if need_file not in files_in_others:
            missing_files.append(need_file)
    if missing_files:
        logging.warning(
            f" не найдены обязательные файлы интеграционных тестов в S3 — {', '.join(missing_files)}"
        )
        pytest.skip(" Тест пропущен. Отсутствуют обязательные файлы")
        return False
    else:
        return True


@pytest.fixture(scope="session", autouse=True)
async def setup_s3(s3_session):
    assert settings.MODE == "TEST"
    assert settings.S3_BUCKET_NAME.endswith("test")
    file_names = await s3_session.books.list_objects_by_prefix("")
    await s3_session.books.delete_bulk(*file_names)


@pytest.fixture(scope="session")
async def register_user(ac_session):
    response = await ac_session.post(
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
async def auth_ac_user(ac_session, register_user):
    response = await ac_session.post(
        url="/auth/login", json={"email": "user@user.com", "password": "string"}
    )
    assert response.status_code == 200
    assert ac_session.cookies
    yield ac_session


@pytest.fixture(scope="session")
async def register_author(ac_session):
    response = await ac_session.post(
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
    logging.info("автор залогинился")
    assert response.status_code == 200


@pytest.fixture(scope="session")
async def auth_ac_author(ac_session, register_author):
    response = await ac_session.post(
        url="/auth/login", json={"email": "author@author.com", "password": "string"}
    )
    assert response.status_code == 200
    assert ac_session.cookies
    yield ac_session
