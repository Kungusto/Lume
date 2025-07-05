from src.repositories.database.base import BaseRepository
from src.models.user_reads import UserBooksReadORM
from src.schemas.user_reads import UserBookRead


class UserBooksReadRepository(BaseRepository):
    model = UserBooksReadORM
    schema = UserBookRead
