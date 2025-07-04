from sqlalchemy import Float, func, select, update, cast
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from src.repositories.database.base import BaseRepository
from src.models.books import BooksORM, BooksTagsORM, GenresORM
from src.schemas.books import (
    Book,
    Tag,
    Genre,
    BookDataWithRels,
    BookDataWithRelsAndAvgRatingPrivat,
    BookDataWithRelsPrivat,
    BookDataWithRelsAndAvgRating,
    GenresBook,
)
from src.models.reviews import ReviewsORM
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

    async def get_one_with_rels(self, privat_data=False, **filter_by):
        query = (
            select(self.model, cast(func.avg(ReviewsORM.rating), Float))
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .filter_by(**filter_by)
            .join(ReviewsORM, ReviewsORM.book_id == BooksORM.book_id, isouter=True)
            .group_by(self.model.book_id)
        )
        result = await self.session.execute(query)
        try:
            model = result.unique().one()
        except NoResultFound as ex:
            raise BookNotFoundException from ex
        if privat_data:
            target_schemaDTO = BookDataWithRelsAndAvgRatingPrivat
            book_schemaDTO = BookDataWithRelsPrivat
        else:
            target_schemaDTO = BookDataWithRelsAndAvgRating
            book_schemaDTO = BookDataWithRels
        print(model)
        return target_schemaDTO(
            **book_schemaDTO.model_validate(
                model[0], from_attributes=True
            ).model_dump(),
            avg_rating=model[1],
        )

    async def get_book_with_rels(self, privat_data=False, **filter_by):
        query = (
            select(self.model, cast(func.avg(ReviewsORM.rating), Float))
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .filter_by(**filter_by)
            .join(ReviewsORM, ReviewsORM.book_id == BooksORM.book_id, isouter=True)
            .group_by(self.model.book_id)
        )
        result = await self.session.execute(query)
        models = result.unique().all()
        if privat_data:
            target_schemaDTO = BookDataWithRelsAndAvgRatingPrivat
            book_schemaDTO = BookDataWithRelsPrivat
        else:
            target_schemaDTO = BookDataWithRelsAndAvgRating
            book_schemaDTO = BookDataWithRels

        return [
            target_schemaDTO(
                **book_schemaDTO.model_validate(
                    book, from_attributes=True
                ).model_dump(),
                avg_rating=avg_rating,
            )
            for book, avg_rating in models
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
        query = (
            select(self.model, cast(func.avg(ReviewsORM.rating), Float))
            .filter_by(is_publicated=True)
            .limit(limit)
            .offset(offset)
            .filter_by(is_publicated=True)
            .options(joinedload(self.model.authors))
            .options(joinedload(self.model.genres))
            .options(joinedload(self.model.tags))
            .options(joinedload(self.model.reviews))
            .join(ReviewsORM, ReviewsORM.book_id == BooksORM.book_id, isouter=True)
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
            query = query.filter(BooksORM.age_limit > search_data.min_age)
        if search_data.max_age:
            query = query.filter(BooksORM.age_limit < search_data.max_age)
        if search_data.later_than:
            query = query.filter(BooksORM.date_publicated > search_data.later_than)

        if search_data.earlier_than:
            query = query.filter(BooksORM.date_publicated < search_data.earlier_than)

        model = await self.session.execute(query)
        results = model.unique().all()
        return [
            BookDataWithRelsAndAvgRating(
                **BookDataWithRels.model_validate(
                    book, from_attributes=True
                ).model_dump(),
                avg_rating=avg_rating,
            )
            for book, avg_rating in results
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

