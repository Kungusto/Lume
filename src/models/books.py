from datetime import date
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped
from src.database import Base
from src.enums.books import LanguagesEnum


class GenresORM(Base) :
    __tablename__ = "Genres"

    genre_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)

class BooksORM(Base) :
    __tablename__ = "Books"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    date_publicated: Mapped[date] = mapped_column(default=lambda: date.today())
    age_limit: Mapped[int]
    title: Mapped[str]
    description: Mapped[str | None]
    language: Mapped[LanguagesEnum] = mapped_column(Enum(LanguagesEnum, name="language_enum"))
    is_rendered: Mapped[bool] = mapped_column(default=False)
    cover_link: Mapped[str | None] = mapped_column(default=None)

class BooksTagsORM(Base) :
    __tablename__ = "Books_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id"))
    title_tag: Mapped[str]

class BooksGenresORM(Base) :
    __tablename__ = "Books_genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id"))
    genre_id: Mapped[int] = mapped_column(ForeignKey("Genres.genre_id"))
