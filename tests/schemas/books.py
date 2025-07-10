from src.schemas.books import Book
from tests.schemas.users import TestUserWithPassword


class TestBookWithRels(Book):
    author: TestUserWithPassword
    genre_id: int
