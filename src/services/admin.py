from datetime import datetime, timezone
from src.schemas.reports import BanAdd
from src.models.reports import BanORM
from src.exceptions.reports import AlreadyBannedException, ReasonAlreadyExistsException, ReasonNotFoundException, ReportNotFoundException, UserNotBannedException
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
        try:
            await self.db.genres.edit(data=data, genre_id=genre_id)
        except AlreadyExistsException as ex:
            raise GenreAlreadyExistsException from ex
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


    async def edit_reason(self, reason_id: int, data):
        try:
            await self.db.reasons.get_one(reason_id=reason_id)
        except ObjectNotFoundException as ex:
            raise ReasonNotFoundException from ex
        try:
            await self.db.reasons.edit(data=data, reason_id=reason_id)
        except AlreadyExistsException as ex:
            raise ReasonAlreadyExistsException from ex
        await self.db.commit()

    async def delete_reason(self, reason_id: int):
        try:
            await self.db.reasons.get_one(reason_id=reason_id)
        except ObjectNotFoundException as ex:
            raise ReasonNotFoundException from ex
        await self.db.reasons.delete(reason_id=reason_id)
        await self.db.commit()


    async def get_not_checked_reports(self):
        return await self.db.reports.get_filtered(is_checked=False)
    

    async def mark_as_checked(self, report_id: int):
        try:
            await self.db.reports.mark_as_checked(report_id=report_id)
        except ObjectNotFoundException as ex:
            raise ReportNotFoundException from ex
        await self.db.commit()   


    async def ban_user_by_id(self, user_id: int, data, user_role):
        try:
            user = await self.db.users.get_one(user_id=user_id)
        except ObjectNotFoundException as ex:
            raise UserNotFoundException from ex
        if await self.db.bans.get_filtered(
            BanORM.ban_until > datetime.now(timezone.utc), user_id=user_id
        ):
            raise AlreadyBannedException
        if user_role == user.role:
            raise ChangePermissionsOfADMINException
        if user.role == "GENERAL_ADMIN":
            raise ChangePermissionsOfADMINException
        # На случай если админ решит понизить другого админа
        ban_data = await self.db.bans.add(data=BanAdd(**data.model_dump(), user_id=user_id))
        await self.db.commit()
        return ban_data
    

    async def unban_user_by_id(self, ban_id: int):
        if not await self.db.bans.get_filtered(ban_id=ban_id):
            raise UserNotBannedException
        await self.db.bans.delete(ban_id=ban_id)
        await self.db.commit()