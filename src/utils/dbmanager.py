from sqlalchemy.ext.asyncio import async_sessionmaker
from src.repositories.database.users import UsersRepository
from src.repositories.database.books import (
    BooksRepository,
    GenresBooksRepository,
    TagRepository,
    GenreRepository,
)
from src.repositories.database.books_authors import BooksAuthorsRepository
from src.repositories.database.reviews import ReviewsRepository
from src.repositories.database.reports import (
    ReportsRepository,
    BansRepository,
    ReasonsRepository,
)


class AsyncDBManager:
    """
    Дополнительный слой абстракции, Позволяющий удобно обращаться к базе данных

    Пример использования:
    ```
    async with AsyncDBManager(session_factory=async_session_maker) as db:
        user = await db.users.get_one(user_id=user_id)
        return user
    ```
    """

    def __init__(self, session_factory: async_sessionmaker):
        """Создает менеджер базы данных с указанной фабрикой"""
        self.session_factory = session_factory

    async def __aenter__(self):
        """Вход в асинхронный контекст with. Создает сессию, и инициализирует репозитории"""
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.books = BooksRepository(self.session)
        self.books_authors = BooksAuthorsRepository(self.session)
        self.books_genres = GenresBooksRepository(self.session)
        self.genres = GenreRepository(self.session)
        self.tags = TagRepository(self.session)
        self.reviews = ReviewsRepository(self.session)
        self.reasons = ReasonsRepository(self.session)
        self.bans = BansRepository(self.session)
        self.reports = ReportsRepository(self.session)

        return self

    async def __aexit__(self, *args):
        """Выход из асинхронного контекста with. Чистит незакоммиченные изменения"""
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        """Сохранения недавних изменений в базу данных"""
        await self.session.commit()


class SyncDBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, *args):
        self.session.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()
