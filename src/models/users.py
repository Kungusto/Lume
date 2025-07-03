from datetime import date
from sqlalchemy import Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String
from src.database import Base
from src.enums.users import AllUsersRolesEnum
import typing

if typing.TYPE_CHECKING:
    from src.models.books import BooksORM


class UsersORM(Base):
    __tablename__ = "Users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[AllUsersRolesEnum] = mapped_column(
        Enum(AllUsersRolesEnum, name="user_role_enum"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str]
    nickname: Mapped[str] = mapped_column(String(30), unique=True)
    last_activity: Mapped[date] = mapped_column(default=lambda: date.today())
    hashed_password: Mapped[str]
    registation_date: Mapped[date] = mapped_column(default=lambda: date.today())

    books: Mapped[list["BooksORM"]] = relationship(  # type: ignore
        back_populates="authors", secondary="Books_authors"
    )
