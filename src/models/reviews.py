from datetime import datetime, timezone
import typing
from sqlalchemy import TIMESTAMP, Integer, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

if typing.TYPE_CHECKING:
    from src.models.books import BooksORM


class ReviewsORM(Base):
    __tablename__ = "Reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer())
    text: Mapped[str] = mapped_column(String(150))
    publication_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("Books.book_id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.user_id", ondelete="CASCADE")
    )

    books: Mapped[list["BooksORM"]] = relationship(  # type: ignore
        "BooksORM", back_populates="reviews"
    )

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range_check"),
    )
