from pydantic import BaseModel
from src.schemas.books import Book
from tests.schemas.users import TestUserWithPassword


class TestBookWithRels(Book):
    author: TestUserWithPassword
    genre_id: int


class TagTitleFromFactory(BaseModel):
    title_tag: str
