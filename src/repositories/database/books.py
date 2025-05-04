from sqlalchemy import insert, select, update
from sqlalchemy.orm import joinedload
from src.repositories.database.base import BaseRepository
from src.models.books import BooksORM, BooksTagsORM, GenresORM
from src.schemas.books import Book, Tag, Genre, BookWithAuthors

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
        return self.schema.model_validate(result, from_attributes=True)

    async def get_book_with_rels(self, **filter_by) : 
        query = select(self.model).options(joinedload(self.model.authors)).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.unique().scalar_one()
        return BookWithAuthors.model_validate(model, from_attributes=True)

class TagRepository(BaseRepository) :
    model = BooksTagsORM
    schema = Tag

class GenreRepository(BaseRepository) :
    model = GenresORM
    schema = Genre
