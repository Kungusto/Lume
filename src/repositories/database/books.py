from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from src.repositories.database.base import BaseRepository
from src.models.books import BooksORM, BooksTagsORM, GenresORM
from src.schemas.books import (
    Book,
    Tag,
    Genre,
    BookDataWithRels,
    BookDataWithRelsPrivat,
    GenresBook,
)
from src.models.books import BooksGenresORM
from src.exceptions.books import BookNotFoundException


class BooksRepository(BaseRepository):
    model = BooksORM
    schema = Book

    async def mark_as_rendered(self, book_id: int):
        update_stmt = (
            update(self.model)
            .filter_by(book_id=book_id)
            .values(is_rendered=True)
            .returning(self.model)
        )
        model = await self.session.execute(update_stmt)
        result = model.scalar_one()
        return self.schema.model_validate(result, from_attributes=True)

    async def mark_as_have_cover(self, book_id: int):
        update_stmt = (
            update(self.model)
            .filter_by(book_id=book_id)
            .values(have_cover=True)
            .returning(self.model)
        )
        model = await self.session.execute(update_stmt)
        result = model.scalars().all()
        return self.schema.model_validate(result, from_attributes=True)

    async def get_book_with_rels(self, privat_data=False, **filter_by):
        query = (
            select(self.model)
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        try:
            model = result.unique().scalar_one()
        except NoResultFound as ex:
            raise BookNotFoundException from ex
        if privat_data:
            return BookDataWithRelsPrivat.model_validate(model, from_attributes=True)
        else:
            return BookDataWithRels.model_validate(model, from_attributes=True)

    async def get_one(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        model = await self.session.execute(query)
        try:
            result = model.scalar_one()
        except NoResultFound as ex:
            raise BookNotFoundException from ex
        return self.schema.model_validate(result, from_attributes=True)

    async def get_filtered_with_pagination(
        self, search_data, limit: int = 0, offset: int = 5
    ):
        query = (
            select(self.model)
            .filter_by(is_publicated=True)
            .limit(limit)
            .offset(offset)
            .filter_by(is_publicated=True)
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .order_by(self.model.book_id)
        )

        if search_data.book_title:
            query = query.filter(
                func.lower(BooksORM.title).contains(
                    search_data.book_title.strip().lower()
                )
            )
        if search_data.min_age:
            query = query.filter(BooksORM.age_limit > search_data.min_age)
        if search_data.max_age:
            query = query.filter(BooksORM.age_limit < search_data.max_age)
        if search_data.later_than:
            query = query.filter(BooksORM.date_publicated > search_data.later_than)

        if search_data.earlier_than:
            query = query.filter(BooksORM.date_publicated < search_data.earlier_than)

        model = await self.session.execute(query)
        results = model.unique().scalars().all()
        return [
            BookDataWithRels.model_validate(result, from_attributes=True)
            for result in results
        ]


class TagRepository(BaseRepository):
    model = BooksTagsORM
    schema = Tag


class GenreRepository(BaseRepository):
    model = GenresORM
    schema = Genre


class GenresBooksRepository(BaseRepository):
    model = BooksGenresORM
    schema = GenresBook
