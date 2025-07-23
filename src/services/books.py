from pydantic import BaseModel
from src.services.base import BaseService
from src.api.dependencies import UserIdDep
from src.utils.helpers import TextFormatingManager
from src.exceptions.books import (
    BookNotFoundException,
    ContentNotFoundException,
    PageNotFoundException,
)
from src.exceptions.search import (
    LaterThanAfterEarlierThanException,
    MinAgeGreaterThanMaxAgeException,
    MinRatingGreaterThanMaxRatingException,
    MinReadersGreaterThanMaxReadersException,
)
from src.exceptions.reports import ReasonNotFoundException
from src.exceptions.base import ObjectNotFoundException, ForeignKeyException
from src.schemas.reports import ReportAdd
from src.schemas.user_reads import UserBookReadAdd, UserBookReadEdit
from src.validation.search import SearchValidator


class BooksService(BaseService):
    async def get_filtered_publicated_books_with_pagination(
        self, search_data, pagination_data
    ):
        try:
            SearchValidator.validate_book_filters(**search_data.model_dump())
        except LaterThanAfterEarlierThanException as ex:
            raise ex
        except MinAgeGreaterThanMaxAgeException as ex:
            raise ex
        except MinRatingGreaterThanMaxRatingException as ex:
            raise ex
        except MinReadersGreaterThanMaxReadersException as ex:
            raise ex

        limit = pagination_data.per_page
        offset = (pagination_data.page - 1) * pagination_data.per_page
        books = await self.db.books.get_filtered_with_pagination(
            limit=limit, offset=offset, search_data=search_data
        )
        for book in books:
            if book.cover_link:
                book.cover_link = await self.s3.books.generate_url(
                    file_path=book.cover_link
                )
        return books

    async def get_all_genres(self):
        return await self.db.genres.get_all()

    async def get_book_by_id(self, book_id: int):
        try:
            return await self.db.books.get_one_with_rels(book_id=book_id)
        except BookNotFoundException as ex:
            raise ex

    async def download_book(self, book_id: int):
        try:
            book = await self.db.books.get_one(book_id=book_id)
        except BookNotFoundException as ex:
            raise ex
        if not book.is_rendered:
            raise ContentNotFoundException
        return await self.s3.books.generate_url(f"books/{book_id}/book.pdf")

    async def get_page(
        self,
        user_id: UserIdDep,
        page_number: int,
        book_id: int,
    ):
        try:
            book = await self.db.books.get_one(book_id=book_id)
        except ObjectNotFoundException as ex:
            raise BookNotFoundException from ex
        try:
            page = await self.db.pages.get_one(book_id=book_id, page_number=page_number)
        except ObjectNotFoundException:
            raise PageNotFoundException(page_number=page_number)
        if not book.is_rendered:
            raise ContentNotFoundException
        if (book.total_pages is None) or (page_number > book.total_pages):
            raise PageNotFoundException(page_number=page_number)
        user_read_book = await self.db.user_reads.get_filtered(
            user_id=user_id, book_id=book_id
        )
        if not user_read_book:
            await self.db.user_reads.add(
                UserBookReadAdd(
                    book_id=book_id, user_id=user_id, last_seen_page=page_number
                )
            )
        else:
            await self.db.user_reads.edit(
                UserBookReadEdit(last_seen_page=page_number),
                user_id=user_id,
                book_id=book_id,
            )
        await self.db.commit()

        page = await self.db.pages.get_one(book_id=book_id, page_number=page_number)
        page_content = page.content
        # Убрать лишние пробелы из текста
        for ind, content_info in enumerate(page_content):
            if content_info["type"] == "image":
                path_in_s3 = content_info["path"]
                access_url = await self.s3.books.generate_url(
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
        return page_content

    async def report_book(self, book_id: int, data: BaseModel):
        try:
            await self.db.books.get_one(book_id=book_id)
        except ObjectNotFoundException as ex:
            raise BookNotFoundException from ex
        try:
            report = await self.db.reports.add(
                data=ReportAdd(**data.model_dump(), book_id=book_id)
            )
        except ForeignKeyException as ex:
            raise ReasonNotFoundException from ex
        await self.db.commit()
        return report
