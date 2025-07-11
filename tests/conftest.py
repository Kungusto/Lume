# ruff: noqa: E402

import asyncio
import json
import logging
import random
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


from src.schemas.books import GenreAdd, GenresBooksAdd
from src.schemas.books_authors import BookAuthorAdd
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
from src.exceptions.conftest import (
    MissingFilesException,
    DirectoryNotFoundException,
    DirectoryIsEmptyException,
)
from tests.factories.users_factory import UserAddFactory, AuthorsAddFactory
from tests.factories.books_factory import BookAddFactory
from tests.schemas.users import TestUserWithPassword
from tests.schemas.books import TestBookWithRels
from tests.utils import ServiceForTests


"""
Напоминания:
id админа = 6
id главного админа = 7
"""

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
            result = await redis.session.ping()
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


# @pytest.fixture(scope="session")
# async def seed_db(setup_database, seed_genres, seed_users, seed_books, seed_reviews):
#     logging.info("База данных заполнена мок-данными!")


@pytest.fixture(scope="session", autouse=True)
async def seed_genres(setup_database):
    logging.debug("Заполняю бд жанрами")
    async with AsyncDBManager(session_factory=async_session_maker_null_pool) as _db:
        with open("tests/mock_genres.json", "r", encoding="utf-8") as file:
            data = [GenreAdd(**genre) for genre in json.load(file)]
            await _db.genres.add_bulk(data)
        await _db.commit()


async def get_db_null_pool():
    async with AsyncDBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db():
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="function")
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
async def check_content_integration_tests():
    checks_config = {
        # С проверкой на наличие определенных файлов
        "check_files": [
            {
                "folder_path": "src/static/books/content",
                "need_files": RequiredFilesForTests.INTEGRATION_TESTS_FILES["content"],
            },
            {
                "folder_path": "src/static/books/covers",
                "need_files": RequiredFilesForTests.INTEGRATION_TESTS_FILES["covers"],
            },
        ],
        # Проверка на наличие хотя-бы одного файла
        "check_not_empty": [
            {"folder_path": "src/static/other"},
        ],
    }
    try:
        for variant in checks_config.get("check_files", []):
            ServiceForTests.check_required_files(
                folder_path=variant.get("folder_path", None),
                need_files=variant.get("need_files", None),
            )
        for variant in checks_config.get("check_not_empty", []):
            ServiceForTests.check_not_empty(
                folder_path=variant.get("folder_path", None)
            )
    except DirectoryNotFoundException as ex:
        pytest.skip(ex.detail)
    except MissingFilesException as ex:
        pytest.skip(ex.detail)
    except DirectoryIsEmptyException as ex:
        pytest.skip(ex.detail)


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


@pytest.fixture(scope="function")
async def auth_ac_user(ac_session, register_user):
    ac_session.cookies.clear()
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
async def auth_ac_author_session(ac_session, register_author):
    response = await ac_session.post(
        url="/auth/login", json={"email": "author@author.com", "password": "string"}
    )
    assert response.status_code == 200
    assert ac_session.cookies
    yield ac_session


@pytest.fixture(scope="session")
async def auth_ac_author(ac_session, register_author):
    ac_session.cookies.clear()
    response = await ac_session.post(
        url="/auth/login", json={"email": "author@author.com", "password": "string"}
    )
    assert response.status_code == 200
    assert ac_session.cookies
    yield ac_session


@pytest.fixture(scope="session")
async def auth_ac_admin(ac_session):
    ac_session.cookies.clear()
    response = await ac_session.post(
        url="/auth/login", json={"email": "admin@admin.com", "password": "admin"}
    )
    assert response.status_code == 200
    assert ac_session.cookies
    yield ac_session


# --- фикстуры для создания нужных нам данных --- #
@pytest.fixture(scope="function")
async def new_user(db):
    user = UserAddFactory()
    user_password = user.hashed_password
    user.hashed_password = AuthService().hash_password(user.hashed_password)
    # добавляем в бд пользователя и получаем его id с прочими данными
    db_user = await db.users.add(user)
    await db.commit()

    return TestUserWithPassword(**db_user.model_dump(), password=user_password)


@pytest.fixture(scope="function")
async def auth_new_user(ac, new_user):
    login_data = {"email": new_user.email, "password": new_user.password}
    response_login = await ac.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac.cookies
    yield ac


@pytest.fixture(scope="function")
async def new_author(db):
    user = AuthorsAddFactory()
    user_password = user.hashed_password
    user.hashed_password = AuthService().hash_password(user.hashed_password)
    # добавляем в бд автора и получаем его id с прочими данными
    db_user = await db.users.add(user)
    await db.commit()
    return TestUserWithPassword(**db_user.model_dump(), password=user_password)


@pytest.fixture(scope="function")
async def auth_new_author(ac, new_author):
    login_data = {"email": new_author.email, "password": new_author.password}
    response_login = await ac.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac.cookies
    yield ac


# --- Книги
@pytest.fixture(scope="function")
async def new_book(db, new_author):
    book = BookAddFactory()
    db_book = await db.books.add(book)
    genre_ids = [g.genre_id for g in await db.genres.get_all()]
    genre_id = random.choice(genre_ids)
    await db.books_genres.add(
        GenresBooksAdd(genre_id=genre_id, book_id=db_book.book_id)
    )
    await db.books_authors.add(
        BookAuthorAdd(book_id=db_book.book_id, author_id=new_author.user_id)
    )
    result_data = TestBookWithRels(
        **db_book.model_dump(), author=new_author, genre_id=genre_id
    )
    await db.commit()
    return result_data


@pytest.fixture(scope="function")
async def authorized_client_with_new_book(new_book, ac):
    login_data = {"email": new_book.author.email, "password": new_book.author.password}
    response_login = await ac.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac.cookies
    yield ac, new_book
