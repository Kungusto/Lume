from fastapi import APIRouter
from src.api.dependencies import (
    PaginationDep,
    DBDep,
    SearchDep,
    S3Dep
)
from src.utils.helpers import PDFRenderer
import fitz

router = APIRouter(prefix="/read", tags=["Чтение книг 📖"])


@router.get("/{book_id}/{page_number}")
async def get_page(
    book_id: int,
    page_number: int,
    s3: S3Dep
): 
    book_file = await s3.books.get_file_by_path(f"books/{book_id}/book.pdf")
    doc = fitz.open(stream=book_file, filetype="pdf")
    content_data = PDFRenderer.parse_text_end_images_from_page(page_number=page_number, book_id=book_id, doc=doc)
    for block in content_data:
        if block["type"] == "image":
            image_path = block["path"]
            new_path = await s3.books.generate_url(file_path=image_path)
            block["path"] = new_path
    return content_data

@router.get("/books")
async def get_all_books_with_pagination(
    pagination_data: PaginationDep,
    search_data: SearchDep,
    db: DBDep
):
    limit = pagination_data.per_page
    offset = (pagination_data.page - 1) * pagination_data.per_page
    return await db.books.get_filtered_with_pagination(limit=limit, offset=offset, search_data=search_data)


@router.get("/genres")
async def get_all_genres(db: DBDep):
    return await db.genres.get_all()