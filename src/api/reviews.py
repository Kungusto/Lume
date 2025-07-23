from fastapi import APIRouter, Path
from src.services.reviews import ReviewsService
from src.api.dependencies import DBDep, UserIdDep, UserRoleDep
from src.schemas.reviews import ReviewAddFromUser, ReviewAdd, ReviewPut
from src.exceptions.reviews import (
    CannotDeleteOthersReviewException,
    CannotEditOthersReviewException,
    RateYourselfException,
    RateYourselfHTTPException,
    ReviewAtThisBookAlreadyExistsException,
    ReviewAtThisBookAlreadyExistsHTTPException,
    ReviewNotFoundException,
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
        await ReviewsService(db=db).edit_review(
           user_id=user_id, 
           user_role=user_role, 
           review_id=review_id, 
           data=data,
        )
    except ReviewNotFoundException as ex:
        raise ReviewNotFoundHTTPException from ex
    except CannotEditOthersReviewException as ex:
        raise CannotEditOthersReviewHTTPException from ex
    return {"status": "OK"}


@router.delete("/{review_id}")
async def delete_review(
    db: DBDep,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    review_id: int = Path(le=2**31),
):
    try:
        await ReviewsService(db=db).delete_review(
           user_id=user_id,
           user_role=user_role,
           review_id=review_id,
        )
    except ReviewNotFoundException as ex:
        raise ReviewNotFoundHTTPException from ex
    except CannotDeleteOthersReviewException as ex:
        raise CannotDeleteOthersReviewHTTPException from ex
    return {"status": "OK"}


@router.get("/my_reviews")
async def get_my_reviews(
    db: DBDep,
    user_id: UserIdDep,
):
    return await ReviewsService(db=db).get_my_reviews(user_id=user_id)

@router.get("/by_book/{book_id}")
async def get_book_reviews(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    return await ReviewsService(db=db).get_book_reviews(book_id=book_id)