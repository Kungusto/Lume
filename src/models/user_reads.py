from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, ForeignKey
from datetime import datetime, timezone
from src.database import Base


class UserBooksReadORM(Base):
    __tablename__ = "User_books_read"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.user_id", ondelete="CASCADE")
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("Books.book_id", ondelete="CASCADE")
    )
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_seen_page: Mapped[int] = mapped_column(default=1)
