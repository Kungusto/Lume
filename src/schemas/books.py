from datetime import date, datetime
import json
from typing import Annotated, List
from pydantic import BaseModel, EmailStr, Field, constr, field_validator, conint
from src.enums.users import AllUsersRolesEnum
from src.enums.books import LanguagesEnum, RenderStatus
from src.schemas.users import User, UserPublicData
from src.schemas.reviews import Review


class Page(BaseModel):
    page_number: int
    book_id: int
    content: str | list[dict]

    @field_validator("content")
    def content_to_str(cls, value: str) -> list[dict]:
        """Преобразуем строку в JSON"""
        if isinstance(value, str):
            return json.loads(value)  # превращаем список в JSON-строку
        return value


class PageAdd(BaseModel):
    page_number: int
    book_id: int
    content: str | list[dict]

    @field_validator("content")
    def content_to_str(cls, value: list[dict]) -> str:
        """Мы будем хранить JSON в виде строки, поэтому требуется преобразование"""
        if isinstance(value, list):
            return json.dumps(
                value, ensure_ascii=False
            )  # превращаем список в JSON-строку
        return value


# Теги
class Tag(BaseModel):
    id: int
    book_id: int
    title_tag: str


class TagAdd(BaseModel):
    book_id: int
    title_tag: str


class TagEdit(BaseModel):
    title_tag: str


# Жанры
class Genre(BaseModel):
    genre_id: int
    title: str


class GenreAdd(BaseModel):
    title: str

    @field_validator("title")
    def first_letter_to_upper(title: str) -> str:
        return title.capitalize() if title else title
    

class GenreEdit(GenreAdd): ...


# M2M Жанров и книг
class GenresBook(BaseModel):
    id: int
    genre_id: int
    book_id: int


class GenresBooksAdd(BaseModel):
    genre_id: int
    book_id: int


# Книги
class BookAuthors(BaseModel):
    authors: list[int]
    book_id: int


class BookAdd(BaseModel):
    title: str
    age_limit: int
    description: str | None
    language: LanguagesEnum


class BookAddWithAuthorsTagsGenres(BookAdd):
    authors: list[int] = []
    genres: list[int] = Field(min_items=1)
    tags: List[constr(min_length=2)] | None = []  # type: ignore

    @field_validator("tags")
    @classmethod
    def tags_to_lower(cls, values: list[str]) -> list[str]:
        return [val.lower() for val in set(values)]


class Book(BaseModel):
    book_id: int
    title: str
    age_limit: Annotated[int, Field(ge=0, le=21)]
    description: str | None
    language: LanguagesEnum
    date_publicated: date
    is_rendered: bool = False
    render_status: RenderStatus | None
    cover_link: str | None = None
    is_publicated: bool
    total_pages: int | None


class BookEditRenderStatus(BaseModel):
    render_status: RenderStatus


class BookPATCHWithRels(BaseModel):
    title: str | None = None
    age_limit: int | None = None
    description: str | None = None
    genres: list[int] | None = []
    tags: List[constr(min_length=2)] | None = []  # type: ignore

    @field_validator("tags")
    @classmethod
    def tags_to_lower(cls, values: list[str] | None = None) -> list[str] | None:
        return [val.lower() for val in values] if values else None


class BookPATCH(BaseModel):
    title: str | None = None
    age_limit: Annotated[conint(ge=0, le=21), None] = None  # type: ignore
    description: str | None = None
    is_publicated: bool | None = None


class BookPUT(BaseModel):
    title: str
    age_limit: Annotated[int, Field(ge=0, le=21)]
    description: str | None


class BookWithAuthors(Book):
    authors: list[User]


class BookPATCHOnPublication(BaseModel):
    is_rendered: bool | None = False
    cover_link: str | None = None


class BookData(Book):
    pages_count: int


class BookDataWithRels(Book):
    authors: list[UserPublicData]  # список авторов
    tags: list[Tag]  # список тегов
    genres: list[Genre]  # список жанров
    reviews: list[Review]  # список отзывов


class BookDataWithRelsPrivat(Book):
    authors: list[User]  # список авторов
    tags: list[Tag]  # список тегов
    genres: list[Genre]  # список жанров
    reviews: list[Review]  # список отзывов


class RatingReadersRel(BaseModel):
    avg_rating: float | None
    readers: int | None


class BookDataWithAllRels(RatingReadersRel, BookDataWithRels):
    pass


class BookDataWithAllRelsPrivat(RatingReadersRel, BookDataWithRelsPrivat):
    pass


class BookDataWithTagRel(BookData):
    tags: list[int]  # список тегов


class BookDataWithGenresRel(BookData):
    genres: list[int]  # список жанров


class FullDataAboutBook(BookData):
    count_readers: int


# Авторы
class UserAndBooksWithRels(BaseModel):
    user_id: int
    role: AllUsersRolesEnum
    email: EmailStr
    name: str
    surname: str
    nickname: str
    last_activity: datetime
    registation_date: datetime
    books: list[BookDataWithRels]
