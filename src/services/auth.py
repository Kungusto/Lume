from src.exceptions.books import (
    BookNotExistsOrYouNotOwnerHTTPException,
)
from src.exceptions.base import PermissionDeniedHTTPException, ObjectNotFoundException
from src.enums.users import AllUsersRolesEnum
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from src.utils.dbmanager import AsyncDBManager
from src.config import settings
import logging
from fastapi import APIRouter, Request, Response
from src.services.base import BaseService
from src.exceptions.base import (
    InternalServerErrorHTTPException,
    ObjectNotFoundException,
    AlreadyExistsException,
)
from src.exceptions.auth import (
    NickAlreadyRegistratedException,
    EmailAlreadyRegistratedHTTPException,
    EmailAlreadyRegistratedException,
    NotAuthentificatedHTTPException,
    NotAuthentificatedException,
    AlreadyAuthentificatedException,
    UserNotFoundException,
    WrongPasswordOrEmailException,
    EmailNotFoundException,
    CannotChangeDataOtherUserException,
)
from src.schemas.users import (
    UserRegistrate,
    UserAdd,
    UserLogin,
    UserPublicData,
    UserPUT,
)
from src.enums.users import AllUsersRolesEnum
from src.utils.cache_manager import get_cache_manager



ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        """Создание токена. В нем будем хранить id и роль пользователя"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        """Декодирование токена"""
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

    def check_permissions(self, role: AllUsersRolesEnum, permission_level: int):
        """Проверяем права на совершение данной операции"""
        user_level = AllUsersRolesEnum.get_permission_level(role)
        if user_level >= permission_level:
            return True
        else:
            raise PermissionDeniedHTTPException

    async def verify_user_owns_book(
        self, user_id: int, book_id: int, db: AsyncDBManager
    ):
        """Проверяем, действительно ли пользователь владеет книгой"""
        try:
            book = await db.books.get_one_with_rels(
                book_id=book_id, privat_data=True
            )  # для того чтобы получить id
        except ObjectNotFoundException as ex:
            raise BookNotExistsOrYouNotOwnerHTTPException from ex
        author_ids = [author.user_id for author in book.authors]
        if user_id not in author_ids:
            raise BookNotExistsOrYouNotOwnerHTTPException
        return book

    async def registrate_user(self, data):
        hashed_password = AuthService().hash_password(data.password)
        data.role = AllUsersRolesEnum(data.role)
        data = UserAdd(**data.model_dump(), hashed_password=hashed_password)
        return await self.db.users.add(data=data)


    async def login_user(self, data, request: Request, response: Response): 
        if request.cookies.get("access_token"):
            raise AlreadyAuthentificatedException
        try:
            user = await self.db.users.get_user_with_hashed_password(email=data.email)
        except EmailNotFoundException as ex:
            raise WrongPasswordOrEmailException from ex
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise WrongPasswordOrEmailException
        access_token = AuthService().create_access_token(
            {"user_id": user.user_id, "role": user.role}
        )
        response.set_cookie(key="access_token", value=access_token)
        return access_token

    async def info_about_current_user(self, user_id: int):
        return await self.db.users.get_one(user_id=user_id)
    
    def logout_user(self, request: Request, response: Response):
        if not request.cookies.get("access_token"):
            raise NotAuthentificatedException
        response.delete_cookie("access_token")

    async def info_about_user(self, user_id: int): 
        try:
            all_data_about_user = await self.db.users.get_one(user_id=user_id)
        except ObjectNotFoundException as ex:
            raise UserNotFoundException from ex
        user_public = UserPublicData(**all_data_about_user.model_dump())
        await self.db.commit()
        return user_public
    
    async def edit_user_data(self, data, user_id, curr_user_id): 
        try:
            await self.db.users.get_one(user_id=user_id)
        except ObjectNotFoundException:
            raise UserNotFoundException
        if user_id != curr_user_id:
            raise CannotChangeDataOtherUserException
        try:
            await self.db.users.edit(user_id=user_id, data=data)
        except AlreadyExistsException as ex:
            raise NickAlreadyRegistratedException from ex
        await self.db.commit()