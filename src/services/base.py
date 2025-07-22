from src.utils.dbmanager import AsyncDBManager

class BaseService:
    def __init__(self, db: AsyncDBManager | None = None):
        self.db = db
