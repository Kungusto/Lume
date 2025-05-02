from repositories.database.base import BaseRepository
from src.models.books import BooksORM, BooksTagsORM, GenresORM
from src.schemas.books import Book, Tag, Genre

class BooksRepository(BaseRepository) :
    model = BooksORM
    schema = Book

class TagRepository(BaseRepository) :
    model = BooksTagsORM
    schema = Tag

class GenreRepository(BaseRepository) :
    model = GenresORM
    schema = Genre
