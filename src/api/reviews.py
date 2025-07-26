from fastapi import APIRouter, Body, Path
from src.services.reviews import ReviewsService
from src.api.dependencies import DBDep, UserIdDep, UserRoleDep
from src.schemas.reviews import ReviewAddFromUser, ReviewPut
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
from src.docs_src.examples.reviews import add_review_example
from src.docs_src.responses.reviews import (
    delete_review_responses,
    add_review_responses,
    edit_review_responses,
    get_book_reviews_responses,
    get_my_reviews_responses,
)

router = APIRouter(prefix="/reviews", tags=["Отзывы на книги 🌟"])


@router.post(
    path="/by_book/{book_id}",
    summary="Опубликовать отзыв на книгу",
    description="Автор не может оценивать свою книгу, "
    "обычные пользователи могут оставить только один отзыв на каждую книгу",
    responses=add_review_responses,
)
async def add_review(
    db: DBDep,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    data: ReviewAddFromUser = Body(openapi_examples=add_review_example),
    book_id: int = Path(le=2**31),
):
    try:
        review = await ReviewsService(db=db).add_review(
            data=data, user_id=user_id, user_role=user_role, book_id=book_id
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ReviewAtThisBookAlreadyExistsException as ex:
        raise ReviewAtThisBookAlreadyExistsHTTPException from ex
    except RateYourselfException as ex:
        raise RateYourselfHTTPException from ex
    return review


@router.put(
    path="/{review_id}",
    summary="Изменить существующий отзыв",
    description="Можно изменить только свой отзыв. "
    "Изменить любой отзыв может только ADMIN и GENERAL_ADMIN",
    responses=edit_review_responses,
)
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


@router.delete(
    path="/{review_id}",
    summary="Удалить отзыв",
    description="Можно изменить только свой отзыв. "
    "Изменить любой отзыв может только ADMIN и GENERAL_ADMIN",
    responses=delete_review_responses,
)
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


@router.get(
    path="/my_reviews",
    summary="Получить все мои отзывы",
    responses=get_my_reviews_responses,
)
async def get_my_reviews(
    db: DBDep,
    user_id: UserIdDep,
):
    return await ReviewsService(db=db).get_my_reviews(user_id=user_id)


@router.get(
    path="/by_book/{book_id}",
    summary="Получить все отзывы на книгу",
    responses=get_book_reviews_responses,
)
async def get_book_reviews(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    return await ReviewsService(db=db).get_book_reviews(book_id=book_id)
