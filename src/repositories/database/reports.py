from datetime import datetime, timezone
from sqlalchemy import func, select, update
from sqlalchemy.exc import NoResultFound
from src.exceptions.base import ObjectNotFoundException
from src.repositories.database.base import BaseRepository
from src.models.reports import BanORM, ReasonsORM, ReportsORM
from src.models.users import UsersORM
from src.schemas.reports import Ban, Reason, Report
from src.schemas.users import UserWithBanDate, User


class BansRepository(BaseRepository):
    model = BanORM
    schema = Ban

    async def get_banned_users(self):
        query = (
            select(UsersORM, func.max(BanORM.ban_until))
            .select_from(BanORM)
            .filter(BanORM.ban_until > datetime.now(timezone.utc))
            .join(UsersORM, UsersORM.user_id == BanORM.user_id)
            .group_by(UsersORM.user_id)
        )
        models = await self.session.execute(query)
        return [
            UserWithBanDate(
                **User.model_validate(user, from_attributes=True).model_dump(),
                ban_until=ban_until,
            )
            for user, ban_until in models.all()
        ]

    async def get_ban_by_user_id(self, user_id: int) -> UserWithBanDate | None:
        now = datetime.now(timezone.utc)
        query = (
            select(UsersORM, func.max(BanORM.ban_until))
            .select_from(BanORM)
            .filter(BanORM.ban_until > now)
            .filter(BanORM.user_id == user_id)
            .join(UsersORM, UsersORM.user_id == BanORM.user_id)
            .group_by(UsersORM.user_id)
        )
        model = await self.session.execute(query)
        row = model.one_or_none()
        if row is None:
            return None
        user, ban_until = row
        return UserWithBanDate(
            **User.model_validate(user, from_attributes=True).model_dump(),
            ban_until=ban_until,
        )


class ReasonsRepository(BaseRepository):
    model = ReasonsORM
    schema = Reason


class ReportsRepository(BaseRepository):
    model = ReportsORM
    schema = Report

    async def mark_as_checked(self, report_id: int):
        update_stmt = (
            update(ReportsORM)
            .filter_by(id=report_id)
            .values(is_checked=True)
            .returning(ReportsORM)
        )
        model = await self.session.execute(update_stmt)
        try:
            return Report.model_validate(model.scalar_one(), from_attributes=True)
        except NoResultFound as ex:
            raise ObjectNotFoundException from ex
