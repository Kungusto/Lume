from datetime import date
from typing import Annotated, List
from pydantic import BaseModel, EmailStr, Field, constr, field_validator, conint
from src.enums.users import AllUsersRolesEnum
from src.enums.books import LanguagesEnum
from src.schemas.users import User, UserPublicData
from src.schemas.reviews import Review

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
    book_id: int
    date_publicated: date
    is_rendered: bool = False
    cover_link: str | None = None
    is_publicated: bool
    total_pages: int | None


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


class BookDataWithRelsAndAvgRating(BookDataWithRels):
    avg_rating: float | None


class BookDataWithRelsPrivat(Book):
    authors: list[User]  # список авторов
    tags: list[Tag]  # список тегов
    genres: list[Genre]  # список жанров
    reviews: list[Review]  # список отзывов


class BookDataWithRelsAndAvgRatingPrivat(BookDataWithRelsPrivat):
    avg_rating: float | None


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
    last_activity: date
    registation_date: date
    books: list[BookDataWithRels]
