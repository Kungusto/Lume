from datetime import datetime, timezone
from src.exceptions.files import StatementNotFoundException
from src.analytics.excel.active_users import UsersDFExcelRepository
from src.repositories.database.utils import AnalyticsQueryFactory
from src.schemas.analytics import UsersStatement, UsersStatementWithoutDate
from src.schemas.reports import BanAdd
from src.models.reports import BanORM
from src.config import settings
from src.exceptions.reports import (
    AlreadyBannedException,
    ReasonAlreadyExistsException,
    ReasonNotFoundException,
    ReportNotFoundException,
    UserNotBannedException,
)
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
        if await self.db.tags.get_filtered(
            book_id=data.book_id, title_tag=data.title_tag
        ):
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
        ban_data = await self.db.bans.add(
            data=BanAdd(**data.model_dump(), user_id=user_id)
        )
        await self.db.commit()
        return ban_data

    async def unban_user_by_id(self, ban_id: int):
        if not await self.db.bans.get_filtered(ban_id=ban_id):
            raise UserNotBannedException
        await self.db.bans.delete(ban_id=ban_id)
        await self.db.commit()

    async def edit_ban_date(self, ban_id: int, data):
        if not await self.db.bans.get_filtered(ban_id=ban_id):
            raise UserNotBannedException
        await self.db.bans.edit(data=data, ban_id=ban_id)
        await self.db.commit()

    async def get_banned_users(self):
        return await self.db.bans.get_banned_users()

    async def generate_report_inside_app(self, data):
        interval = data.interval
        now = datetime.now()
        date_template = "%Y-%m-%d_%H-%M-%S"
        analytics_query = AnalyticsQueryFactory.users_data_sql(
            now=now, interval_td=interval
        )
        model = await self.db.session.execute(analytics_query)
        data = UsersStatementWithoutDate.model_validate(
            model.first(), from_attributes=True
        )
        stmt_path = (
            f"{settings.STATEMENT_DIR_PATH}/users_{now.strftime(date_template)}.xlsx"
        )
        result = UsersStatement(
            **data.model_dump(),
            stmt_path=stmt_path,
            started_date_as_str=(now - interval).strftime(date_template),
            ended_date_as_str=now.strftime(date_template),
        )
        excel_doc = UsersDFExcelRepository(
            f"{settings.STATEMENT_DIR_PATH}/users_{now.strftime(date_template)}.xlsx"
        )
        excel_doc.add(result)
        excel_doc.commit()
        excel_bytes = excel_doc.to_bytes()
        await self.s3.analytics.save_statement(
            key=f"analytics/{now.strftime('%Y-%m-%d')}/users_{now.strftime(date_template)}.xlsx",
            body=excel_bytes,
        )
        return result

    async def get_statements_by_date(self, statement_date):
        statemenets = await self.s3.analytics.list_objects_by_prefix(
            f"analytics/{statement_date.strftime('%Y-%m-%d')}"
        )
        urls = []
        for statement in statemenets:
            key_url = await self.s3.analytics.generate_url(file_path=statement)
            urls.append({"key": statement, "url": key_url})
        return urls

    async def save_and_get_auto_statement(self):
        key = f"analytics/auto/{datetime.today().strftime('%Y-%m-%d_%H-%M')}"
        try:
            with open(
                f"{settings.STATEMENT_DIR_PATH}/users_statement_auto.xlsx", "rb"
            ) as doc:
                content = doc.read()
                if not content:
                    raise StatementNotFoundException
                doc.seek(0)
                await self.s3.analytics.save_statement(key=key, body=doc)
        except FileNotFoundError as ex:
            raise StatementNotFoundException from ex
        # Делаем файл пустым
        with open(f"{settings.STATEMENT_DIR_PATH}/users_statement_auto.xlsx", "w") as f:
            f.truncate(0)
        return await self.s3.analytics.generate_url(file_path=key)
