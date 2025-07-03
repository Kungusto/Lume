from fastapi import APIRouter, Path
from src.api.dependencies import PaginationDep, DBDep, SearchDep, S3Dep
from src.utils.helpers import PDFRenderer
from src.exceptions.books import (
    BookNotFoundHTTPException,
    BookNotFoundException,
    ContentNotFoundHTTPException,
    PageNotFoundException,
    PageNotFoundHTTPException,
    ContentOrBookNotFoundHTTPException,
)
from src.exceptions.reports import ReasonNotFoundHTTPException
from src.exceptions.base import ObjectNotFoundException, ForeignKeyException
from src.exceptions.files import FileNotFoundException
from src.schemas.reports import ReportAdd, ReportAddFromUser
import fitz

router = APIRouter(prefix="/books", tags=["Чтение книг 📖"])


@router.get("")
async def get_filtered_publicated_books_with_pagination(
    pagination_data: PaginationDep, search_data: SearchDep, db: DBDep, s3: S3Dep
):
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
        return await db.books.get_book_with_rels(book_id=book_id)
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
async def get_page(
    s3: S3Dep,
    page_number: int = Path(le=5000),
    book_id: int = Path(le=2**31),
):
    try:
        book_file = await s3.books.get_file_by_path(f"books/{book_id}/book.pdf")
    except FileNotFoundException as ex:
        raise ContentOrBookNotFoundHTTPException from ex
    doc = fitz.open(stream=book_file, filetype="pdf")
    try:
        content_data = PDFRenderer.parse_text_end_images_from_page(
            page_number=page_number, book_id=book_id, doc=doc
        )
    except PageNotFoundException as ex:
        raise PageNotFoundHTTPException(page_number=page_number) from ex
    for block in content_data:
        if block["type"] == "image":
            image_path = block["path"]
            new_path = await s3.books.generate_url(file_path=image_path)
            block["path"] = new_path
    return content_data


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
