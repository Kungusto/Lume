from src.exceptions.books import (
    CannotDeleteGenreException,
    GenreAlreadyExistsException,
    GenreNotFoundException,
)
from src.exceptions.auth import (
    ChangePermissionsOfADMINException,
    UserNotFoundException,
)
from src.exceptions.base import (
    AlreadyExistsException,
    ObjectNotFoundException,
    ForeignKeyException,
)
from src.services.base import BaseService


class AdminService(BaseService):
    async def change_role(
        self,
        data,
        current_user_role,
        user_id: int,
    ):
        try:
            user = await self.db.users.get_one(user_id=user_id)
        except ObjectNotFoundException as ex:
            raise UserNotFoundException from ex

        # На случай если админ решит понизить другого админа
        if current_user_role == user.role or user.role == "GENERAL_ADMIN":
            raise ChangePermissionsOfADMINException

        await self.db.users.edit(data=data, user_id=user_id)
        await self.db.commit()

    async def add_genre(self, data):
        try:
            genre = await self.db.genres.add(data=data)
        except AlreadyExistsException as ex:
            raise GenreAlreadyExistsException from ex
        await self.db.commit()
        return genre

    async def edit_genre(self, data, genre_id: int):
        try:
            await self.db.genres.get_one(genre_id=genre_id)
        except ObjectNotFoundException as ex:
            raise GenreNotFoundException from ex
        await self.db.genres.edit(data=data, genre_id=genre_id)
        await self.db.commit()

    async def delete_genre(self, genre_id: int):
        try:
            await self.db.genres.get_one(genre_id=genre_id)
        except ObjectNotFoundException as ex:
            raise GenreNotFoundException from ex
        try:
            await self.db.genres.delete(genre_id=genre_id)
        except ForeignKeyException as ex:
            raise CannotDeleteGenreException from ex
        await self.db.commit()
