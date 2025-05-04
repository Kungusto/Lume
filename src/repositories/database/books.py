from sqlalchemy import insert, select, update
from src.repositories.database.base import BaseRepository
from src.models.books import BooksORM, BooksTagsORM, GenresORM
from src.schemas.books import Book, Tag, Genre

class BooksRepository(BaseRepository) :
    model = BooksORM
    schema = Book


    async def mark_as_rendered(self, book_id: int) : 
        update_stmt = (
            update(self.model)
            .filter_by(book_id=book_id)
            .values(is_rendered=True)
            .returning(self.model)
            )
        model = await self.session.execute(update_stmt)
        result = model.scalar_one()
        return self.schema.model_validate(result, from_attributes=True)


    async def mark_as_have_cover(self, book_id: int) : 
        update_stmt = (
            update(self.model)
            .filter_by(book_id=book_id)
            .values(have_cover=True)
            .returning(self.model)
            )
        model = await self.session.execute(update_stmt)
        result = model.scalars().all()
        return self.schema.model_validate(result)


class TagRepository(BaseRepository) :
    model = BooksTagsORM
    schema = Tag

class GenreRepository(BaseRepository) :
    model = GenresORM
    schema = Genre
