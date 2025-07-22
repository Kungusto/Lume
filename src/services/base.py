from src.utils.dbmanager import AsyncDBManager


class BaseService:
    def __init__(self, db: AsyncDBManager | None = None, s3 = None):
        self.db = db
        self.s3 = s3
