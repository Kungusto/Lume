import logging
from fastapi import APIRouter, Request, Response
from src.exceptions.base import (
    InternalServerErrorHTTPException,
    ObjectNotFoundException,
    PermissionDeniedHTTPException,
)
from src.exceptions.auth import (
    NickAlreadyRegistratedHTTPException,
    NickAlreadyRegistratedException,
    EmailAlreadyRegistratedHTTPException,
    EmailAlreadyRegistratedException,
    NotAuthentificatedHTTPException,
    AlreadyAuthentificatedHTTPException,
    UserNotFoundHTTPException,
    WrongPasswordOrEmailHTTPException,
    EmailNotFoundException,
)
from src.schemas.users import (
    UserRegistrate,
    UserAdd,
    UserLogin,
    UserPublicData,
    UserPUT,
)
from src.api.dependencies import DBDep, UserIdDep
from src.services.auth import AuthService
from src.enums.users import AllUsersRolesEnum

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация 🔐"])


@router.post("/register")
async def registrate_users(data: UserRegistrate, db: DBDep):
    hashed_password = AuthService().hash_password(data.password)
    data.role = AllUsersRolesEnum(data.role.value)
    data = UserAdd(**data.model_dump(), hashed_password=hashed_password)
    try:
        result = await db.users.add(data=data)
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
async def login_user(data: UserLogin, db: DBDep, response: Response, request: Request):
    if request.cookies.get("access_token"):
        raise AlreadyAuthentificatedHTTPException
    try:
        user = await db.users.get_user_with_hashed_password(email=data.email)
    except EmailNotFoundException as ex:
        raise WrongPasswordOrEmailHTTPException from ex
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise WrongPasswordOrEmailHTTPException
    access_token = AuthService().create_access_token(
        {"user_id": user.user_id, "role": str(user.role)}
    )
    response.set_cookie(key="access_token", value=access_token)
    return {"access_token": access_token}


@router.get("/me")
async def info_about_current_user(user_id: UserIdDep, db: DBDep):
    user = await db.users.get_one(user_id=user_id)
    return user


@router.post("/logout")
async def exit_from_account(response: Response, request: Request):
    if not request.cookies.get("access_token"):
        raise NotAuthentificatedHTTPException
    response.delete_cookie("access_token")
    return {"status": "OK"}


@router.get("/{user_id}")
async def info_about_user(db: DBDep, user_id: int):
    try:
        all_data_about_user = await db.users.get_one(user_id=user_id)
    except ObjectNotFoundException as ex:
        raise UserNotFoundHTTPException from ex
    user_public = UserPublicData(**all_data_about_user.model_dump())
    await db.commit()
    return user_public


@router.put("/{user_id}")
async def edit_user_data(
    db: DBDep, data: UserPUT, user_id: int, curr_user_id: UserIdDep
):
    if user_id != curr_user_id:
        raise PermissionDeniedHTTPException
    await db.users.edit(user_id=user_id, data=data)
    await db.commit()
    return {"status": "OK"}
