from src.exceptions.books import (
    BookNotExistsOrYouNotOwnerHTTPException,
)
from src.exceptions.base import PermissionDeniedHTTPException
from src.enums.users import AllUsersRolesEnum
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt
from src.utils.dbmanager import AsyncDBManager
from src.config import settings

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        "Создание токена. В нем будем хранить id и роль пользователя"
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
        book = await db.books.get_book_with_rels(
            book_id=book_id, privat_data=True
        )  # для того чтобы получить id
        author_ids = [author.user_id for author in book.authors]
        if user_id not in author_ids:
            raise BookNotExistsOrYouNotOwnerHTTPException
        return book
