from src.exceptions.base import (
    AlreadyExistsException,
    AlreadyExistsHTTPException,
    PermissionDeniedHTTPException,
    ObjectNotFoundHTTPException,
)


class ReviewAtThisBookAlreadyExistsException(AlreadyExistsException):
    detail = "Вы не можете публиковать несколько отзывов на одну книгу"


class ReviewAtThisBookAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Вы не можете публиковать несколько отзывов на одну книгу"


class RateYourselfHTTPException(PermissionDeniedHTTPException):
    detail = "Вы не можете публиковать отзывы на собственные книги"


class ReviewNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Отзыв не найден"


class CannotEditOthersReviewHTTPException(PermissionDeniedHTTPException):
    detail = "Вы не можете редактировать чужые отзывы"


class CannotDeleteOthersReviewHTTPException(PermissionDeniedHTTPException):
    detail = "Вы не можете удалять чужые отзывы"
