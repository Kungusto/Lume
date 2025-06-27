from src.exceptions.base import (
    ObjectNotFoundHTTPException,
    AlreadyExistsHTTPException,
    PermissionDeniedHTTPException,
    ObjectNotFoundException,
)


class BookNotFoundException(ObjectNotFoundException):
    detail = "Книга не найдена"


class GenreNotFoundException(ObjectNotFoundException):
    detail = "Жанр не найден"


class GenreNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Жанр не найден"


class CoverNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "К этой книге пока нету обложек"


class BookNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Книга не найдена"


class ContentAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Контент книги уже был опубликован"


class CoverAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Обложка книги уже была опубликована"


class BookAlreadyPublicatedHTTPException(AlreadyExistsHTTPException):
    detail = "Книга уже опубликована"


class BookNotExistsOrYouNotOwnerHTTPException(PermissionDeniedHTTPException):
    detail = "Книга не существует, либо у вас нет доступа к ее изменению"

