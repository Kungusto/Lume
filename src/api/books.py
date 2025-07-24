from fastapi import APIRouter, Path
from src.api.dependencies import PaginationDep, DBDep, S3Dep, UserIdDep, SearchDep
from src.exceptions.books import (
    BookNotFoundHTTPException,
    BookNotFoundException,
    ContentNotFoundException,
    ContentNotFoundHTTPException,
    PageNotFoundException,
    PageNotFoundHTTPException,
)
from src.exceptions.search import (
    LaterThanAfterEarlierThanException,
    LaterThanAfterEarlierThanHTTPException,
    MinAgeGreaterThanMaxAgeException,
    MinAgeGreaterThanMaxAgeHTTPException,
    MinRatingGreaterThanMaxRatingException,
    MinRatingGreaterThanMaxRatingHTTPException,
    MinReadersGreaterThanMaxReadersException,
    MinReadersGreaterThanMaxReadersHTTPException,
)
from src.exceptions.reports import ReasonNotFoundException, ReasonNotFoundHTTPException
from src.schemas.reports import ReportAddFromUser
from src.utils.cache_manager import get_cache_manager
from src.services.books import BooksService

router = APIRouter(prefix="/books", tags=["Чтение книг 📖"])
cache = get_cache_manager()


@router.get("")
@cache.base()
async def get_filtered_publicated_books_with_pagination(
    db: DBDep,
    s3: S3Dep,
    pagination_data: PaginationDep,
    search_data: SearchDep,
):
    try:
        books = await BooksService(
            db=db, s3=s3
        ).get_filtered_publicated_books_with_pagination(
            pagination_data=pagination_data,
            search_data=search_data,
        )
    except LaterThanAfterEarlierThanException as ex:
        raise LaterThanAfterEarlierThanHTTPException from ex
    except MinAgeGreaterThanMaxAgeException as ex:
        raise MinAgeGreaterThanMaxAgeHTTPException from ex
    except MinRatingGreaterThanMaxRatingException as ex:
        raise MinRatingGreaterThanMaxRatingHTTPException from ex
    except MinReadersGreaterThanMaxReadersException as ex:
        raise MinReadersGreaterThanMaxReadersHTTPException from ex
    return books


@router.get("/genres")
async def get_all_genres(db: DBDep):
    return await BooksService(db=db).get_all_genres()


@router.get("/{book_id}")
async def get_book_by_id(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    try:
        book = await BooksService(db=db).get_book_by_id(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    return book


@router.get("/download/{book_id}")
async def download_book(
    s3: S3Dep,
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    try:
        url = await BooksService(db=db, s3=s3).download_book(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ContentNotFoundException as ex:
        raise ContentNotFoundHTTPException from ex
    return url


@router.get("/{book_id}/page/{page_number}")
@cache.books.page(ttl=300)
async def get_page(
    s3: S3Dep,
    db: DBDep,
    user_id: UserIdDep,
    page_number: int = Path(le=5000),
    book_id: int = Path(le=2**31),
):
    try:
        page = await BooksService(db=db, s3=s3).get_page(
            user_id=user_id,
            page_number=page_number,
            book_id=book_id,
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ContentNotFoundException as ex:
        raise ContentNotFoundHTTPException from ex
    except PageNotFoundException as ex:
        raise PageNotFoundHTTPException(page_number=page_number) from ex
    return page


@router.post("/{book_id}/report")
async def report_book(
    db: DBDep,
    data: ReportAddFromUser,
    book_id: int = Path(le=2**31),
):
    try:
        report = await BooksService(db=db).report_book(book_id=book_id, data=data)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ReasonNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    return report
