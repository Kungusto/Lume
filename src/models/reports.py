from datetime import datetime, timedelta
from sqlalchemy import ForeignKey
from src.database import Base
from sqlalchemy.orm import mapped_column, Mapped


class BanORM(Base):
    __tablename__ = "Banned_Users"

    ban_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.user_id"))
    ban_until: Mapped[datetime] = mapped_column(default=lambda: datetime.now() + timedelta(hours=1))
    comment: Mapped[str | None] = mapped_column(default=None)


class ReasonsORM(Base):
    __tablename__ = "Book_reasons"

    reason_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]


class ReportsORM(Base):
    __tablename__ = "Book_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id"))
    reason_id: Mapped[int] = mapped_column(ForeignKey("Book_reasons.reason_id"))