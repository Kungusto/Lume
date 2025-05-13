from src.repositories.database.users import UsersRepository
from src.repositories.database.books import (
    BooksRepository,
    GenresBooksRepository,
    TagRepository,
)
from src.repositories.database.books_authors import BooksAuthorsRepository
from src.repositories.database.files_src_images import FilesRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.books = BooksRepository(self.session)
        self.books_authors = BooksAuthorsRepository(self.session)
        self.files = FilesRepository(self.session)
        self.books_genres = GenresBooksRepository(self.session)
        self.tags = TagRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
