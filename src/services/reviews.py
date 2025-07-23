from src.services.base import BaseService
from fastapi import APIRouter, Path
from src.api.dependencies import DBDep, UserIdDep, UserRoleDep
from src.schemas.reviews import ReviewAddFromUser, ReviewAdd, ReviewPut
from src.exceptions.reviews import (
    RateYourselfException,
    RateYourselfHTTPException,
    ReviewAtThisBookAlreadyExistsException,
    ReviewAtThisBookAlreadyExistsHTTPException,
    ReviewNotFoundHTTPException,
    CannotEditOthersReviewHTTPException,
    CannotDeleteOthersReviewHTTPException,
)
from src.exceptions.books import BookNotFoundException, BookNotFoundHTTPException
from src.exceptions.base import ObjectNotFoundException


class ReviewsService(BaseService):
    async def add_review(self, user_role: str, book_id: int, user_id: int, data):
        try:
            book = await self.db.books.get_one_with_rels(book_id=book_id, privat_data=True)
        except BookNotFoundException as ex:
            raise ex
        if user_role not in ["ADMIN", "GENERAL_ADMIN"]:
            authors_ids = [author.user_id for author in book.authors]
            if user_id in authors_ids:
                raise RateYourselfException
            if await self.db.reviews.get_filtered(book_id=book_id, user_id=user_id):
                raise ReviewAtThisBookAlreadyExistsException
        review = await self.db.reviews.add(
            data=ReviewAdd(
                **data.model_dump(),
                user_id=user_id,
                book_id=book_id,
            )
        )
        await self.db.commit()
        return review