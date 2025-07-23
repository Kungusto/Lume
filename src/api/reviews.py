from fastapi import APIRouter, Path
from src.services.reviews import ReviewsService
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

router = APIRouter(prefix="/reviews", tags=["Отзывы на книги 🌟"])


@router.post("/by_book/{book_id}")
async def add_review(
    db: DBDep,
    data: ReviewAddFromUser,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    book_id: int = Path(le=2**31),
):
    try:
        review = await ReviewsService(db=db).add_review(data=data, user_id=user_id, user_role=user_role, book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ReviewAtThisBookAlreadyExistsException as ex:
        raise ReviewAtThisBookAlreadyExistsHTTPException from ex
    except RateYourselfException as ex:
        raise RateYourselfHTTPException from ex
    return review


@router.put("/{review_id}")
async def edit_review(
    data: ReviewPut,
    db: DBDep,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    review_id: int = Path(le=2**31),
):
    try:
        review = await db.reviews.get_one(review_id=review_id)
    except ObjectNotFoundException as ex:
        raise ReviewNotFoundHTTPException from ex
    if user_role not in ["ADMIN", "GENERAL_ADMIN"]:
        if user_id != review.user_id:
            raise CannotEditOthersReviewHTTPException
    await db.reviews.edit(data=data, review_id=review_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{review_id}")
async def delete_review(
    db: DBDep,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    review_id: int = Path(le=2**31),
):
    try:
        review = await db.reviews.get_one(review_id=review_id)
    except ObjectNotFoundException as ex:
        raise ReviewNotFoundHTTPException from ex
    if user_role not in ["ADMIN", "GENERAL_ADMIN"]:
        if user_id != review.user_id:
            raise CannotDeleteOthersReviewHTTPException
    await db.reviews.delete(review_id=review_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/my_reviews")
async def get_my_reviews(
    db: DBDep,
    user_id: UserIdDep,
):
    return await db.reviews.get_filtered(user_id=user_id)


@router.get("/by_book/{book_id}")
async def get_book_reviews(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    return await db.reviews.get_filtered(book_id=book_id)
