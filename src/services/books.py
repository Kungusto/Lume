from src.services.base import BaseService
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

class BooksService(BaseService):
    async def get_filtered_publicated_books_with_pagination(self, search_data, pagination_data):
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
                book.cover_link = await self.s3.books.generate_url(file_path=book.cover_link)
        return books