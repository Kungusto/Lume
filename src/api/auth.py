import logging
from fastapi import APIRouter, Body, Path, Request, Response
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
    User,
    UserPublicData,
    UserRegistrate,
    UserLogin,
    UserPUT,
)
from src.api.dependencies import DBDep, UserIdDep
from src.services.auth import AuthService
from src.utils.cache_manager import get_cache_manager
from src.docs_src.examples.auth import register_example, login_example, edit_example
from src.docs_src.responses.auth import (
    register_responses,
    login_responses,
    info_current_user_responses,
    logout_responses,
    info_about_user_responses,
    edit_user_data_responses,
)


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация 🔐"])
cache = get_cache_manager()


@router.post(
    path="/register",
    summary="Регистрация пользователей 🔑",
    description="Регистрирует пользователей и авторов",
    responses=register_responses,
    response_model=User,
)
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
    return result


@router.post(
    path="/login",
    summary="Логин пользователя",
    description="Проверяет почту и пароль на соответствие. Если все ОК - сохраняет в cookies access_token пользователя",
    responses=login_responses,
)
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


@router.get(
    path="/me",
    summary="Получение данных о себе",
    description="Считывает user_id из cookies, а затем ищет данные об этом пользователе в бд",
    responses=info_current_user_responses,
    response_model=User,
)
async def info_about_current_user(user_id: UserIdDep, db: DBDep):
    return await AuthService(db=db).info_about_current_user(user_id=user_id)


@router.post(
    path="/logout",
    summary="Выход из аккаунта",
    description="Удаляет access_token из cookie файлов",
    responses=logout_responses,
)
async def exit_from_account(request: Request, response: Response):
    try:
        AuthService().logout_user(request=request, response=response)
    except NotAuthentificatedException as ex:
        raise NotAuthentificatedHTTPException from ex
    return {"status": "OK"}


@router.get(
    path="/{user_id}",
    summary="Получение публичных данных о пользователе",
    description="Поиск имени, фамилии и ника пользователя по id",
    responses=info_about_user_responses,
    response_model=UserPublicData,
)
@cache.base()
async def info_about_user(db: DBDep, user_id: int = Path(le=2**31)):
    try:
        user = await AuthService(db=db).info_about_user(user_id=user_id)
    except UserNotFoundException as ex:
        raise UserNotFoundHTTPException from ex
    return user


@router.put(
    path="/{user_id}",
    summary="Изменить публичные данные",
    description="Пользователь может изменять только свои данные, админ - любые",
    responses=edit_user_data_responses,
)
async def edit_user_data(
    db: DBDep,
    curr_user_id: UserIdDep,
    user_id: int = Path(le=2**31),
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
