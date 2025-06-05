from sqlalchemy import insert, select, update
from datetime import date
from sqlalchemy.orm import joinedload
from src.exceptions.auth import (
    EmailAlreadyRegistratedException,
    NickAlreadyRegistratedException,
    EmailNotFoundException,
)
from src.repositories.database.base import BaseRepository
from src.models.users import UsersORM
from src.schemas.books import UserWithBooks
from src.schemas.users import User, UserWithHashedPassword, UserRegistrate
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError, NoResultFound


class UsersRepository(BaseRepository):
    model = UsersORM
    schema = User

    async def get_user_with_hashed_password(self, email):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        try:
            user = result.scalar_one()
        except NoResultFound:
            raise EmailNotFoundException
        return UserWithHashedPassword.model_validate(user, from_attributes=True)

    async def add(self, data: UserRegistrate):
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(add_stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):
                msg = str(exc.orig)
                if "Users_nickname_key" in msg:  # ник уже занят
                    raise NickAlreadyRegistratedException
                elif "Users_email_key" in msg:  # почта уже зарегестрирована
                    raise EmailAlreadyRegistratedException

        model = result.scalars().first()
        return self.schema.model_validate(model, from_attributes=True)

    async def get_books_by_user(self, user_id: int):
        query = (
            select(self.model)
            .options(joinedload(self.model.books))
            .filter_by(user_id=user_id)
        )
        result = await self.session.execute(query)
        models = result.unique().scalars().all()
        return [
            UserWithBooks.model_validate(model, from_attributes=True)
            for model in models
        ]

    async def update_user_activity(self, user_id: int):
        query = (
            update(self.model)
            .filter_by(user_id=user_id)
            .values(last_activity=date.today())
        )
        result = await self.session.execute(query)
        model = result.scalar_one()
        return User.model_validate(model, from_attributes=True)
