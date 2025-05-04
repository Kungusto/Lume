from sqlalchemy import insert, select
from src.exceptions.exceptions import EmailAlreadyRegistratedException, NickAlreadyRegistratedException
from src.repositories.database.base import BaseRepository
from src.models.users import UsersORM
from src.schemas.users import User, UserWithHashedPassword, UserRegistrate
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError

class UsersRepository(BaseRepository) :
    model = UsersORM
    schema = User

    async def get_user_with_hashed_password(self, email) :
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        user = result.scalar_one()
        return UserWithHashedPassword.model_validate(user, from_attributes=True)
    
    async def add(self, data: UserRegistrate) : 
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try :
            result = await self.session.execute(add_stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):
                msg = str(exc.orig)
                if "Users_nickname_key" in msg:
                    raise NickAlreadyRegistratedException
                elif "Users_email_key" in msg:
                    raise EmailAlreadyRegistratedException

        model = result.scalars().first()
        return self.schema.model_validate(model, from_attributes=True)