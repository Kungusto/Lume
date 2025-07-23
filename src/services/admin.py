from src.exceptions.reports import ReasonAlreadyExistsException
from src.exceptions.books import (
    BookNotFoundException,
    CannotDeleteGenreException,
    GenreAlreadyExistsException,
    GenreNotFoundException,
    TagAlreadyExistsException,
    TagNotFoundException,
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

    
    async def add_tag(self, data):
        try:
            await self.db.books.get_one(book_id=data.book_id)
        except ObjectNotFoundException as ex:
            raise BookNotFoundException from ex
        if await self.db.tags.get_filtered(book_id=data.book_id, title_tag=data.title_tag):
            raise TagAlreadyExistsException
        tag = await self.db.tags.add(data=data)
        await self.db.commit()
        return tag
    

    async def delete_tag(self, tag_id: int): 
        try:
            await self.db.tags.get_one(id=tag_id)
        except ObjectNotFoundException as ex:
            raise TagNotFoundException from ex
        await self.db.tags.delete(id=tag_id)
        await self.db.commit()

    
    async def edit_tag(self, tag_id: int, data):
        try:
            await self.db.tags.get_one(id=tag_id)
        except ObjectNotFoundException as ex:
            raise TagNotFoundException from ex
        await self.db.tags.edit(data=data, id=tag_id)
        await self.db.commit()


    async def add_reason(self, data):
        try:
            reason = await self.db.reasons.add(data)
        except AlreadyExistsException as ex:
            raise ReasonAlreadyExistsException from ex
        await self.db.commit()
        return reason
