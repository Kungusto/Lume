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


# Мокирование декораторов кеша
from unittest import mock
from tests.mock.cache import fake_cache_by_key

mock.patch("src.decorators.cache.utils.cache_by_key", fake_cache_by_key).start()

from src.schemas.books import GenreAdd, GenresBooksAdd, BookPATCH, TagAdd
from src.schemas.books_authors import BookAuthorAdd
from src.schemas.reports import ReportAdd, BanAdd
from src.services.auth import AuthService
from src.api.dependencies import get_db
from src.database import async_session_maker_null_pool, engine_null_pool, Base
from src.utils.dbmanager import AsyncDBManager
from src.config import Settings
from src.main import app
from src.utils.s3_manager import AsyncS3Client
from src.constants.files import RequiredFilesForTests
from src.tasks.celery_app import celery_app
from src.exceptions.conftest import (
    MissingFilesException,
    DirectoryNotFoundException,
    DirectoryIsEmptyException,
)
from tests.factories.users_factory import (
    UserAddFactory,
    AuthorsAddFactory,
    AdminAddFactory,
    GeneralAdminAddFactory,
)
from tests.factories.books_factory import BookAddFactory
from tests.factories.reviews_factory import ReviewAddFactory
from tests.factories.genres_factory import GenreAddFactory
from tests.factories.tags_factory import TagAddFactory
from tests.factories.reasons_factory import ReasonAddFactory
from tests.factories.reports_factory import ReportAddFactory
from tests.factories.bans_factory import BanAddFactory
from tests.schemas.users import TestUserWithPassword, TestBanInfo
from tests.schemas.books import TestBookWithRels
from tests.schemas.reviews import TestReviewWithRels
from tests.utils import ServiceForTests


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


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

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
async def check_content_for_tests():
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
    # Проверка путей генерации отчетов
    assert settings.STATEMENT_DIR_PATH == "tests/analytics/data"
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
async def new_user_with_ac(ac, new_user):
    login_data = {"email": new_user.email, "password": new_user.password}
    response_login = await ac.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac.cookies
    yield ac, new_user


@pytest.fixture(scope="function")
async def new_general_admin(db):
    user = GeneralAdminAddFactory()
    user_password = user.hashed_password
    user.hashed_password = AuthService().hash_password(user.hashed_password)
    # добавляем в бд пользователя и получаем его id с прочими данными
    db_user = await db.users.add(user)
    await db.commit()

    return TestUserWithPassword(**db_user.model_dump(), password=user_password)


@pytest.fixture(scope="function")
async def auth_new_user(ac, new_user):
    ac.cookies.clear()
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


@pytest.fixture(scope="function")
async def new_admin(db):
    admin = AdminAddFactory()
    admin_password = admin.hashed_password
    admin.hashed_password = AuthService().hash_password(admin.hashed_password)
    # добавляем в бд автора и получаем его id с прочими данными
    db_admin = await db.users.add(admin)
    await db.commit()
    return TestUserWithPassword(**db_admin.model_dump(), password=admin_password)


@pytest.fixture(scope="function")
async def auth_new_admin(ac, new_admin):
    login_data = {"email": new_admin.email, "password": new_admin.password}
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


@pytest.fixture(scope="function")
async def authorized_client_new_book_with_content(authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book
    file, filename = await ServiceForTests.get_file_and_name(
        "books/content/test_book_2.pdf"
    )
    response_add_content = await author_client.post(
        url=f"/author/content/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_content.status_code == 200
    return author_client, book


@pytest.fixture(scope="function")
async def new_publicated_book(db, new_book):
    updated_data = BookPATCH(is_publicated=True)
    await db.books.edit(updated_data, is_patch=True, book_id=new_book.book_id)
    await db.commit()
    return new_book


@pytest.fixture(scope="function")
async def new_publicated_book_with_cover(
    db, authorized_client_with_new_book_with_cover
):
    _, book = authorized_client_with_new_book_with_cover
    updated_data = BookPATCH(is_publicated=True)
    await db.books.edit(updated_data, is_patch=True, book_id=book.book_id)
    await db.commit()
    return book


@pytest.fixture(scope="function")
async def authorized_client_with_new_book_with_cover(authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book

    file, filename = await ServiceForTests.get_file_and_name(
        "books/covers/normal_cover.jpg"
    )
    response_add_cover = await author_client.post(
        url=f"author/cover/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_cover.status_code == 200
    yield author_client, book


# -- Отзывы
@pytest.fixture(scope="function")
async def new_review(new_book, auth_new_user):
    review = ReviewAddFactory()
    response_add = await auth_new_user.post(
        url=f"/reviews/by_book/{new_book.book_id}",
        json=review.model_dump(),
    )
    assert response_add.status_code == 200
    response_json = response_add.json()
    review_to_return = TestReviewWithRels(
        book_id=new_book.book_id,
        user_id=response_json.get("user_id", None),
        text=response_json.get("text", None),
        rating=response_json.get("rating", None),
        publication_date=response_json.get("publication_date", None),
        review_id=response_json.get("review_id", None),
    )
    yield review_to_return


@pytest.fixture(scope="function")
async def new_review_with_author_ac(new_book, auth_new_user):
    review = ReviewAddFactory()
    response_add = await auth_new_user.post(
        url=f"/reviews/by_book/{new_book.book_id}",
        json=review.model_dump(),
    )
    assert response_add.status_code == 200
    response_json = response_add.json()
    review_to_return = TestReviewWithRels(
        book_id=new_book.book_id,
        user_id=response_json.get("user_id", None),
        text=response_json.get("text", None),
        rating=response_json.get("rating", None),
        publication_date=response_json.get("publication_date", None),
        review_id=response_json.get("review_id", None),
    )
    yield auth_new_user, review_to_return


# -- Жанры
@pytest.fixture(scope="function")
async def new_genre(db):
    genre = GenreAddFactory()
    db_genre = await db.genres.add(genre)
    await db.commit()
    return db_genre


# -- Теги
@pytest.fixture(scope="function")
async def new_tag(db, new_book):
    tag = TagAddFactory()
    tag_add = TagAdd(title_tag=tag.title_tag, book_id=new_book.book_id)
    db_tag = await db.tags.add(tag_add)
    await db.commit()
    return db_tag


# -- Причины банов
@pytest.fixture(scope="function")
async def new_reason(db):
    reason = ReasonAddFactory()
    db_reason = await db.reasons.add(reason)
    await db.commit()
    return db_reason


# -- Жалобы
@pytest.fixture(scope="function")
async def new_report(db, new_book, new_reason):
    # фабрика возвращает pydantic-модель. берем ее атрибут comment
    comment_from_factory = ReportAddFactory().comment
    report_to_add = ReportAdd(
        reason_id=new_reason.reason_id,
        book_id=new_book.book_id,
        comment=comment_from_factory,
    )
    db_report = await db.reports.add(report_to_add)
    await db.commit()
    return db_report


# -- Забаненный пользователь
@pytest.fixture(scope="function")
async def ban_info():
    return BanAddFactory()


@pytest.fixture(scope="function")
async def new_banned_user(db, ban_info):
    user = UserAddFactory()
    user_password = user.hashed_password
    user.hashed_password = AuthService().hash_password(user_password)
    # добавляем в бд пользователя и получаем его id с прочими данными
    db_user = await db.users.add(user)
    db_ban = await db.bans.add(
        BanAdd(
            **ban_info.model_dump(),
            user_id=db_user.user_id,
        )
    )
    await db.commit()

    return TestBanInfo(
        ban_id=db_ban.ban_id,
        user_id=db_user.user_id,
        comment=ban_info.comment,
        ban_until=ban_info.ban_until,
    )


# -- Второй клиент
@pytest.fixture(scope="function")
async def ac2():
    """
    Дополнительная сессия для второго клиента
    Нужна для избегания конфликта с первой
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac2:
        yield ac2


@pytest.fixture(scope="function")
async def new_second_user(db):
    """
    Создаёт второго пользователя в базе для тестов.
    Используется, когда нужен пользователь, отличный от первого.
    """
    user = UserAddFactory()
    user_password = user.hashed_password
    user.hashed_password = AuthService().hash_password(user.hashed_password)
    # добавляем в бд пользователя и получаем его id с прочими данными
    db_user = await db.users.add(user)
    await db.commit()

    return TestUserWithPassword(**db_user.model_dump(), password=user_password)


@pytest.fixture(scope="function")
async def auth_new_second_user(ac2, new_second_user):
    login_data = {"email": new_second_user.email, "password": new_second_user.password}
    response_login = await ac2.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac2.cookies
    yield ac2


@pytest.fixture(scope="function")
async def new_second_user_with_ac(ac2, new_second_user):
    login_data = {"email": new_second_user.email, "password": new_second_user.password}
    response_login = await ac2.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac2.cookies
    yield ac2, new_second_user


@pytest.fixture(scope="function")
async def new_second_admin(db):
    user = AdminAddFactory()
    user_password = user.hashed_password
    user.hashed_password = AuthService().hash_password(user.hashed_password)
    # добавляем в бд автора и получаем его id с прочими данными
    db_user = await db.users.add(user)
    await db.commit()
    return TestUserWithPassword(**db_user.model_dump(), password=user_password)


@pytest.fixture(scope="function")
async def auth_new_second_admin(ac2, new_second_admin):
    login_data = {
        "email": new_second_admin.email,
        "password": new_second_admin.password,
    }
    response_login = await ac2.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac2.cookies
    yield ac2
