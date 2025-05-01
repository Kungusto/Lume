from fastapi import Depends, Request
from typing import Annotated
from src.database import async_session_maker
from src.utils.dbmanager import DBManager
from src.services.auth import AuthService
from src.exceptions.exceptions import NotAuthentificatedHTTPException, ExpireTokenHTTPException
from jwt.exceptions import ExpiredSignatureError

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
