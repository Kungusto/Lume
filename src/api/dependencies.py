from fastapi import Depends, Request
from typing import Annotated
from jwt.exceptions import ExpiredSignatureError
from src.database import async_session_maker, async_session_maker_null_pool
from src.utils.dbmanager import DBManager
from src.services.auth import AuthService
from src.exceptions.auth import (
    NotAuthentificatedHTTPException,
    ExpireTokenHTTPException,
)
from src.utils.s3_manager import S3Client
from src.config import settings
from src.connectors.redis_connector import RedisManager
from src.enums.users import AllUsersRolesEnum


# --- Authentification ---


def get_token(request: Request):
    access_token = request.cookies.get("access_token", None)
    if not access_token:
        raise NotAuthentificatedHTTPException
    return access_token


def user_id_from_token(access_token=Depends(get_token)):
    try:
        data = AuthService().decode_token(access_token)
    except ExpiredSignatureError:
        raise ExpireTokenHTTPException
    return data.get("user_id", None)


def user_role_from_token(access_token=Depends(get_token)):
    try:
        data = AuthService().decode_token(access_token)
    except ExpiredSignatureError:
        raise ExpireTokenHTTPException
    return data.get("role", None)


UserIdDep = Annotated[int, Depends(user_id_from_token)]

UserRoleDep = Annotated[AllUsersRolesEnum, Depends(user_role_from_token)]

# --- Authorization ---


def authorize_and_return_user_id(min_level: int) -> int:
    async def check(user_id: UserIdDep, user_role: UserRoleDep):
        """
        Всего есть три уровня доступа:
            1. Пользователь: 1
            2. Автор: 2
            3. Админ: 3

        В каждой ручке указываем минимально допустимый
        уровень доступа для доступа
        """
        AuthService().check_permissions(role=user_role, permission_level=min_level)
        return user_id

    return Depends(check)


# --- Database ---


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


def get_db_manager_np():
    return DBManager(session_factory=async_session_maker_null_pool)


async def get_db_np():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


# --- S3 Client ---


def get_s3client():
    return S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_URL,
        region_name=settings.S3_REGION
    )


async def get_session():
    async with get_s3client() as client:
        yield client


S3Dep = Annotated[S3Client, Depends(get_session)]


# --- Redis ---


def get_redisMan():
    return RedisManager(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


async def get_session_redis():
    async with get_redisMan() as redis:
        yield redis


RedisDep = Annotated[RedisManager, Depends(get_session_redis)]
