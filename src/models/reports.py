from datetime import datetime, timedelta
from sqlalchemy import TIMESTAMP, ForeignKey
from src.database import Base
from sqlalchemy.orm import mapped_column, Mapped


class BanORM(Base):
    __tablename__ = "Banned_Users"

    ban_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.user_id"))
    ban_until: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now() + timedelta(hours=1),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(default=None)


class ReasonsORM(Base):
    __tablename__ = "Book_reasons"

    reason_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)


class ReportsORM(Base):
    __tablename__ = "Book_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id"))
    reason_id: Mapped[int] = mapped_column(ForeignKey("Book_reasons.reason_id"))
    comment: Mapped[str | None] = mapped_column(default=None)
    is_checked: Mapped[bool] = mapped_column(default=False, nullable=False)
