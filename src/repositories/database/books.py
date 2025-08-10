from sqlalchemy import Float, func, select, update, cast
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from src.repositories.database.base import BaseRepository
from src.models.books import BooksORM, BooksTagsORM, GenresORM, PageORM, BooksGenresORM
from src.models.user_reads import UserBooksReadORM
from src.schemas.books import (
    Book,
    Tag,
    Genre,
    BookDataWithRels,
    BookDataWithAllRelsPrivat,
    BookDataWithRelsPrivat,
    BookDataWithAllRels,
    BookRenderStatus,
    GenresBook,
    Page,
)
from src.models.reviews import ReviewsORM
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

    async def get_one_with_rels(self, privat_data=False, **filter_by):
        avg_rating = cast(func.avg(ReviewsORM.rating), Float).label("rating")
        readers = func.count(UserBooksReadORM.user_id.distinct()).label("readers")
        query = (
            select(self.model, avg_rating, readers)
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .filter_by(**filter_by)
            .join(ReviewsORM, ReviewsORM.book_id == BooksORM.book_id, isouter=True)
            .join(
                UserBooksReadORM,
                UserBooksReadORM.book_id == BooksORM.book_id,
                isouter=True,
            )
            .group_by(self.model.book_id)
        )
        result = await self.session.execute(query)
        try:
            model = result.unique().one()
        except NoResultFound as ex:
            raise BookNotFoundException from ex
        book, avg_rating, readers = model
        if privat_data:
            target_schemaDTO = BookDataWithAllRelsPrivat
            book_schemaDTO = BookDataWithRelsPrivat
        else:
            target_schemaDTO = BookDataWithAllRels
            book_schemaDTO = BookDataWithRels
        return target_schemaDTO(
            **book_schemaDTO.model_validate(book, from_attributes=True).model_dump(),
            avg_rating=avg_rating,
            readers=readers,
        )

    async def get_book_with_rels(self, privat_data=False, **filter_by):
        avg_rating = cast(func.avg(ReviewsORM.rating), Float).label("rating")
        readers = func.count(UserBooksReadORM.user_id.distinct()).label("readers")
        query = (
            select(self.model, avg_rating, readers)
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .filter_by(**filter_by)
            .join(ReviewsORM, ReviewsORM.book_id == BooksORM.book_id, isouter=True)
            .join(
                UserBooksReadORM,
                UserBooksReadORM.book_id == BooksORM.book_id,
                isouter=True,
            )
            .group_by(self.model.book_id)
        )
        result = await self.session.execute(query)
        models = result.unique().all()
        if privat_data:
            target_schemaDTO = BookDataWithAllRelsPrivat
            book_schemaDTO = BookDataWithRelsPrivat
        else:
            target_schemaDTO = BookDataWithAllRels
            book_schemaDTO = BookDataWithRels

        return [
            target_schemaDTO(
                **book_schemaDTO.model_validate(
                    book, from_attributes=True
                ).model_dump(),
                avg_rating=avg_rating,
                readers=readers,
            )
            for book, avg_rating, readers in models
        ]

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
        avg_rating = cast(func.avg(ReviewsORM.rating), Float).label("rating")
        readers = func.count(UserBooksReadORM.user_id.distinct()).label("readers")
        query = (
            select(self.model, avg_rating, readers)
            .filter_by(is_publicated=True)
            .limit(limit)
            .offset(offset)
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .join(ReviewsORM, ReviewsORM.book_id == BooksORM.book_id, isouter=True)
            .join(
                UserBooksReadORM,
                UserBooksReadORM.book_id == BooksORM.book_id,
                isouter=True,
            )
            .order_by(self.model.book_id)
            .group_by(self.model.book_id)
        )

        if search_data.book_title:
            query = query.filter(
                func.lower(BooksORM.title).contains(
                    search_data.book_title.strip().lower()
                )
            )
        if search_data.min_age:
            query = query.filter(BooksORM.age_limit >= search_data.min_age)
        if search_data.max_age:
            query = query.filter(BooksORM.age_limit <= search_data.max_age)
        if search_data.later_than:
            query = query.filter(BooksORM.date_publicated >= search_data.later_than)
        if search_data.earlier_than:
            query = query.filter(BooksORM.date_publicated <= search_data.earlier_than)
        if search_data.min_rating:
            query = query.having(avg_rating >= search_data.min_rating)
        if search_data.max_rating:
            query = query.having(avg_rating <= search_data.max_rating)
        if search_data.min_readers:
            query = query.having(readers >= search_data.min_readers)
        if search_data.max_readers:
            query = query.having(readers <= search_data.max_readers)

        model = await self.session.execute(query)
        results = model.unique().all()
        return [
            BookDataWithAllRels(
                **BookDataWithRels.model_validate(
                    book, from_attributes=True
                ).model_dump(),
                avg_rating=avg_rating,
                readers=readers,
            )
            for book, avg_rating, readers in results
        ]
    
    async def get_render_status(self, book_id: int):
        query = select(self.model).filter_by(book_id=book_id)
        model = await self.session.execute(query)
        try:
            result = model.scalar_one()
        except NoResultFound as ex:
            raise BookNotFoundException from ex
        return BookRenderStatus.model_validate(result, from_attributes=True)

class TagRepository(BaseRepository):
    model = BooksTagsORM
    schema = Tag


class GenreRepository(BaseRepository):
    model = GenresORM
    schema = Genre


class GenresBooksRepository(BaseRepository):
    model = BooksGenresORM
    schema = GenresBook


class PageRepository(BaseRepository):
    model = PageORM
    schema = Page
