from sqlalchemy import Integer, CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class ReviewsORM(Base):
    __tablename__ = "Reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(Integer())
    text: Mapped[str] = mapped_column(String(150))
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.user_id", ondelete="CASCADE"))

    books: Mapped[list["BooksORM"]] = relationship( # type: ignore
        "BooksORM", back_populates="reviews"
    )

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range_check"),
    )