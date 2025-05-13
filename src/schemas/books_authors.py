from pydantic import BaseModel


class BookAuthor(BaseModel):
    id: int
    book_id: int
    author_id: int


class BookAuthorAdd(BaseModel):
    book_id: int
    author_id: int
