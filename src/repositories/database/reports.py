from sqlalchemy import select, update
from src.repositories.database.base import BaseRepository
from src.models.reports import BanORM, ReasonsORM, ReportsORM
from src.models.users import UsersORM
from src.schemas.reports import Ban, Reason, Report
from src.schemas.users import User


class BansRepository(BaseRepository):
    model = BanORM
    schema = Ban

    async def get_banned_users(self): 
        query = (
            select(UsersORM)
            .select_from(BanORM)
            .join(UsersORM, UsersORM.user_id == BanORM.user_id)
            .group_by(UsersORM.user_id)
        )
        models = await self.session.execute(query)
        return [
            User.model_validate(model, from_attributes=True) for model in models.scalars().all()
        ]


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
        return Report.model_validate(model.scalar_one(), from_attributes=True)
    

