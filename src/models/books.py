from datetime import date
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.database import Base
from src.enums.books import LanguagesEnum
import typing

if typing.TYPE_CHECKING:
    from src.models.users import UsersORM


class GenresORM(Base):
    __tablename__ = "Genres"

    genre_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)

    books: Mapped[list["BooksORM"]] = relationship(
        back_populates="genres", secondary="Books_genres"
    )


class BooksORM(Base):
    __tablename__ = "Books"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    date_publicated: Mapped[date] = mapped_column(default=lambda: date.today())
    age_limit: Mapped[int]
    title: Mapped[str]
    description: Mapped[str | None]
    language: Mapped[LanguagesEnum] = mapped_column(
        Enum(LanguagesEnum, name="language_enum")
    )
    is_rendered: Mapped[bool] = mapped_column(default=False)
    cover_link: Mapped[str | None] = mapped_column(default=None)
    is_publicated: Mapped[bool] = mapped_column(default=False)

    authors: Mapped[list["UsersORM"]] = relationship(  # type: ignore
        back_populates="books", secondary="Books_authors"
    )
    tags: Mapped[list["BooksTagsORM"]] = relationship(  # type: ignore
        "BooksTagsORM", back_populates="books"
    )
    genres: Mapped[list["GenresORM"]] = relationship(  # type: ignore
        back_populates="books", secondary="Books_genres"
    )
    reviews: Mapped[list["ReviewsORM"]] = relationship( # type: ignore
        "ReviewsORM", back_populates="books"
    )


class BooksTagsORM(Base):
    __tablename__ = "Books_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("Books.book_id", ondelete="CASCADE")
    )
    title_tag: Mapped[str]

    books: Mapped[list["BooksORM"]] = relationship(  # type: ignore
        "BooksORM", back_populates="tags"
    )


class BooksGenresORM(Base):
    __tablename__ = "Books_genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("Books.book_id", ondelete="CASCADE")
    )
    genre_id: Mapped[int] = mapped_column(ForeignKey("Genres.genre_id"))
