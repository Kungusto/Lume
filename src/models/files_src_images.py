from src.database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey

class FilesSrcORM(Base) :
    __tablename__ = "FilesSrc"
    
    file_id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("Books.book_id"))
    src: Mapped[str]