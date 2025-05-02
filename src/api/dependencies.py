from fastapi import Depends, Request
from typing import Annotated
from jwt.exceptions import ExpiredSignatureError
from src.database import async_session_maker
from src.utils.dbmanager import DBManager
from src.services.auth import AuthService
from src.exceptions.exceptions import NotAuthentificatedHTTPException, ExpireTokenHTTPException
from src.services.s3_manager import S3Client
from src.config import settings

def get_token(request: Request) : 
    access_token = request.cookies.get("access_token", None)
    if not access_token :
        raise NotAuthentificatedHTTPException
    return access_token

def user_id_from_token(access_token=Depends(get_token)) :
    try :
        data = AuthService().decode_token(access_token) 
    except ExpiredSignatureError :
        raise ExpireTokenHTTPException
    return data.get("user_id", None)

UserIdDep = Annotated[int, Depends(user_id_from_token)]

def get_db_manager() : 
    return DBManager(session_factory=async_session_maker)

async def get_db() :
    async with get_db_manager() as db :
        yield db

DBDep = Annotated[DBManager, Depends(get_db)]

def get_s3client() :
    return S3Client(
        access_key=settings.S3_ACCESS_KEY,         
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_URL
    )

async def get_session() :
    async with get_s3client() as client :
        yield client

S3Dep = Annotated[S3Client, Depends(get_session)]