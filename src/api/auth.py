import logging
from fastapi import APIRouter, Body, Request, Response
from src.exceptions.base import (
    InternalServerErrorHTTPException,
)
from src.exceptions.auth import (
    NickAlreadyRegistratedHTTPException,
    NickAlreadyRegistratedException,
    EmailAlreadyRegistratedHTTPException,
    EmailAlreadyRegistratedException,
    NotAuthentificatedHTTPException,
    NotAuthentificatedException,
    AlreadyAuthentificatedHTTPException,
    AlreadyAuthentificatedException,
    UserNotFoundHTTPException,
    WrongPasswordOrEmailHTTPException,
    WrongPasswordOrEmailException,
    CannotChangeDataOtherUserException,
    CannotChangeDataOtherUserHTTPException,
    UserNotFoundException,
)
from src.schemas.users import (
    UserRegistrate,
    UserLogin,
    UserPUT,
)
from src.api.dependencies import DBDep, UserIdDep
from src.services.auth import AuthService
from src.utils.cache_manager import get_cache_manager
from src.examples.users import register_example, login_example, edit_example


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация 🔐"])
cache = get_cache_manager()


@router.post("/register")
async def registrate_user(
    db: DBDep,
    data: UserRegistrate = Body(openapi_examples=register_example), 
):
    try:
        result = await AuthService(db=db).registrate_user(data=data)
    except NickAlreadyRegistratedException as ex:
        raise NickAlreadyRegistratedHTTPException from ex
    except EmailAlreadyRegistratedException as ex:
        raise EmailAlreadyRegistratedHTTPException from ex
    except Exception as ex:
        logging.exception(ex)
        raise InternalServerErrorHTTPException
    await db.commit()
    return {"status": "OK", "data": result}


@router.post("/login")
async def login_user(
    db: DBDep, 
    request: Request, 
    response: Response,
    data: UserLogin = Body(openapi_examples=login_example), 
):
    try:
        access_token = await AuthService(db=db).login_user(
            data=data, request=request, response=response
        )
    except AlreadyAuthentificatedException as ex:
        raise AlreadyAuthentificatedHTTPException from ex
    except WrongPasswordOrEmailException as ex:
        raise WrongPasswordOrEmailHTTPException from ex
    return {"access_token": access_token}


@router.get("/me")
async def info_about_current_user(user_id: UserIdDep, db: DBDep):
    return await AuthService(db=db).info_about_current_user(user_id=user_id)


@router.post("/logout")
async def exit_from_account(request: Request, response: Response):
    try:
        AuthService().logout_user(request=request, response=response)
    except NotAuthentificatedException as ex:
        raise NotAuthentificatedHTTPException from ex
    return {"status": "OK"}


@router.get("/{user_id}")
@cache.base()
async def info_about_user(db: DBDep, user_id: int):
    try:
        user = await AuthService(db=db).info_about_user(user_id=user_id)
    except UserNotFoundException as ex:
        raise UserNotFoundHTTPException from ex
    return user


@router.put("/{user_id}")
async def edit_user_data(
    db: DBDep, 
    user_id: int, 
    curr_user_id: UserIdDep,
    data: UserPUT = Body(openapi_examples=edit_example), 
):
    try:
        await AuthService(db=db).edit_user_data(
            data=data, user_id=user_id, curr_user_id=curr_user_id
        )
    except UserNotFoundException as ex:
        raise UserNotFoundHTTPException from ex
    except CannotChangeDataOtherUserException as ex:
        raise CannotChangeDataOtherUserHTTPException from ex
    except NickAlreadyRegistratedException as ex:
        raise NickAlreadyRegistratedHTTPException from ex
    return {"status": "OK"}
