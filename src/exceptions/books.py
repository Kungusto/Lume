from src.exceptions.base import (
    ObjectNotFoundHTTPException,
    AlreadyExistsHTTPException,
    AlreadyExistsException,
    PermissionDeniedException,
    PermissionDeniedHTTPException,
    ObjectNotFoundException,
    LumeHTTPException,
)


class BookNotFoundException(ObjectNotFoundException):
    detail = "Книга не найдена"


class GenreNotFoundException(ObjectNotFoundException):
    detail = "Жанр не найден"


class GenreNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Жанр не найден"


class CoverNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Обложка не найдена"


class BookNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Книга не найдена"


class ContentNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Контент книги не найден"


class ContentOrBookNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Книга не найдена, либо ее контент не опубликован"


class PageNotFoundException(ObjectNotFoundException):
    def __init__(self, page_number, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.detail = f"Страница {page_number} не найдена"


class PageNotFoundHTTPException(ObjectNotFoundHTTPException):
    def __init__(self, page_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detail = f"Страница {page_number} не найдена"


class AuthorNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Автор не найден"


class AuthorNotFoundException(ObjectNotFoundException):
    detail = "Автор не найден"


class ContentAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Контент книги уже был опубликован"


class CoverAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Обложка книги уже была опубликована"


class BookAlreadyPublicatedHTTPException(AlreadyExistsHTTPException):
    detail = "Книга уже опубликована"


class BookNotExistsOrYouNotOwnerHTTPException(PermissionDeniedHTTPException):
    detail = "Книга не существует, либо у вас нет доступа к ее изменению"


class BookNotExistsOrYouNotOwnerException(PermissionDeniedException):
    detail = "Книга не существует, либо у вас нет доступа к ее изменению"


class GenreAlreadyExistsException(AlreadyExistsException):
    detail = "Жанр с таким названием уже существует"


class GenreAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Жанр с таким названием уже существует"


class TagNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Тег не найден"


class TagAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Нельзя добавить два одинаковых тега на одну книгу"


class UnableToPuslishHTTPException(LumeHTTPException):
    detail = "Невозможно опубликовать. Не выполнены требования для публикации"
    status_code = 422
