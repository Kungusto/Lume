from src.repositories.database.base import BaseRepository
from src.models.reports import BanORM, ReasonsORM, ReportsORM
from src.schemas.reports import Ban, Reason, Report


class BansRepository(BaseRepository):
    model = BanORM
    schema = Ban


class ReasonsRepository(BaseRepository):
    model = ReasonsORM
    schema = Reason


class ReportsRepository(BaseRepository):
    model = ReportsORM
    schema = Report
