from fastapi import APIRouter, Body, Path
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
from src.docs_src.examples.books import report_book_example
from src.docs_src.responses.books import (
    download_book_responses,
    get_all_genres_responses,
    get_book_by_id_responses,
    get_filtered_publicated_books_with_pagination_responses,
    get_page_responses,
    report_book_responses,
)


router = APIRouter(prefix="/books", tags=["Чтение книг 📖"])
cache = get_cache_manager()


@router.get(path="", summary="Получить список книг по фильтрам", responses=get_filtered_publicated_books_with_pagination_responses)
@cache.base(ttl=15)
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


@router.get(path="/genres", summary="Список всех жанров", responses=get_all_genres_responses)
async def get_all_genres(db: DBDep):
    return await BooksService(db=db).get_all_genres()


@router.get(path="/{book_id}", summary="Получить книгу по её id", responses=get_book_by_id_responses)
async def get_book_by_id(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    try:
        book = await BooksService(db=db).get_book_by_id(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    return book


@router.get(
    path="/download/{book_id}",
    summary="Скачать книгу по её id",
    description="Возвращает URL доступа для скачивания нужной книги",
    responses=download_book_responses
)
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


@router.get(
    path="/{book_id}/page/{page_number}",
    summary="Получить страницу книги",
    description="Возвращает массив из элементов с подробной информацией о каждой строчке в книге. "
    "Если встречаются изображения - возвращает URL доступа на их скачивание",
    responses=get_page_responses
)
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


@router.post(
    path="/{book_id}/report",
    summary="Пожаловаться на книгу",
    description="Все жалобы будут видны админу",
    responses=report_book_responses
)
async def report_book(
    db: DBDep,
    data: ReportAddFromUser = Body(openapi_examples=report_book_example),
    book_id: int = Path(le=2**31),
):
    try:
        report = await BooksService(db=db).report_book(book_id=book_id, data=data)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ReasonNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    return report
