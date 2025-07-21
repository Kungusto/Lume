from fastapi import APIRouter, Path
from src.api.dependencies import PaginationDep, DBDep, S3Dep, UserIdDep, SearchDep
from src.utils.helpers import TextFormatingManager
from src.exceptions.books import (
    BookNotFoundHTTPException,
    BookNotFoundException,
    ContentNotFoundHTTPException,
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
from src.exceptions.reports import ReasonNotFoundHTTPException
from src.exceptions.base import ObjectNotFoundException, ForeignKeyException
from src.schemas.reports import ReportAdd, ReportAddFromUser
from src.schemas.user_reads import UserBookReadAdd, UserBookReadEdit
from src.validation.search import SearchValidator
from src.utils.cache_manager import get_cache_manager

router = APIRouter(prefix="/books", tags=["Чтение книг 📖"])
cache = get_cache_manager()


@router.get("")
async def get_filtered_publicated_books_with_pagination(
    pagination_data: PaginationDep,
    db: DBDep,
    s3: S3Dep,
    search_data: SearchDep,
):
    try:
        SearchValidator.validate_book_filters(**search_data.model_dump())
    except LaterThanAfterEarlierThanException as ex:
        raise LaterThanAfterEarlierThanHTTPException from ex
    except MinAgeGreaterThanMaxAgeException as ex:
        raise MinAgeGreaterThanMaxAgeHTTPException from ex
    except MinRatingGreaterThanMaxRatingException as ex:
        raise MinRatingGreaterThanMaxRatingHTTPException from ex
    except MinReadersGreaterThanMaxReadersException as ex:
        raise MinReadersGreaterThanMaxReadersHTTPException from ex

    limit = pagination_data.per_page
    offset = (pagination_data.page - 1) * pagination_data.per_page
    books = await db.books.get_filtered_with_pagination(
        limit=limit, offset=offset, search_data=search_data
    )
    for book in books:
        if book.cover_link:
            book.cover_link = await s3.books.generate_url(file_path=book.cover_link)
    return books


@router.get("/genres")
async def get_all_genres(db: DBDep):
    return await db.genres.get_all()


@router.get("/{book_id}")
async def get_book_by_id(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    try:
        return await db.books.get_one_with_rels(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex


@router.get("/download/{book_id}")
async def download_book(
    s3: S3Dep,
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    try:
        book = await db.books.get_one(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    if not book.is_rendered:
        raise ContentNotFoundHTTPException
    return await s3.books.generate_url(f"books/{book_id}/book.pdf")


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
        book = await db.books.get_one(book_id=book_id)
    except ObjectNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    if not book.is_rendered:
        raise ContentNotFoundHTTPException
    if (book.total_pages is None) or (page_number > book.total_pages):
        raise PageNotFoundHTTPException(page_number=page_number)
    user_read_book = await db.user_reads.get_filtered(user_id=user_id, book_id=book_id)
    if not user_read_book:
        await db.user_reads.add(
            UserBookReadAdd(
                book_id=book_id, user_id=user_id, last_seen_page=page_number
            )
        )
    else:
        await db.user_reads.edit(
            UserBookReadEdit(last_seen_page=page_number),
            user_id=user_id,
            book_id=book_id,
        )
    await db.commit()

    page = await db.pages.get_one(book_id=book_id, page_number=page_number)
    page_content = page.content
    # Убрать лишние пробелы из текста
    for ind, content_info in enumerate(page_content):
        if content_info["type"] == "image":
            path_in_s3 = content_info["path"]
            access_url = await s3.books.generate_url(
                file_path=path_in_s3,
                expires_in=60 * 60 * 24,  # 1 день
            )
            content_info["path"] = access_url
        else:
            content_info["content"] = TextFormatingManager.replace_nbsp(
                content_info["content"]
            )
        page_content[ind] = content_info

    page.content = page_content
    return page


@router.post("/{book_id}/report")
async def report_book(
    db: DBDep,
    data: ReportAddFromUser,
    book_id: int = Path(le=2**31),
):
    try:
        await db.books.get_one(book_id=book_id)
    except ObjectNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    try:
        report = await db.reports.add(
            data=ReportAdd(**data.model_dump(), book_id=book_id)
        )
    except ForeignKeyException as ex:
        raise ReasonNotFoundHTTPException from ex
    await db.commit()
    return report
