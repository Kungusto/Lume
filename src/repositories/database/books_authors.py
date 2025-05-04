from src.repositories.database.base import BaseRepository
from src.models.books_authors import BooksAuthorsORM
from src.schemas.books_authors import BookAuthor

class BooksAuthorsRepository(BaseRepository) :
    model = BooksAuthorsORM
    schema = BookAuthor