from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column 
from sqlalchemy import ForeignKey

class BooksAuthorsORM(Base) :
    __tablename__ = "Books_authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("Users.user_id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id"))
    
