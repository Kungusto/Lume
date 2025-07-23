from src.exceptions.base import (
    AlreadyExistsException,
    AlreadyExistsHTTPException,
    ObjectNotFoundException,
    ObjectNotFoundHTTPException,
    LumeHTTPException,
)


class ReasonAlreadyExistsHTTPException(AlreadyExistsHTTPException):
    detail = "Эта причина уже добавлена"


class ReasonAlreadyExistsException(AlreadyExistsException):
    detail = "Эта причина уже добавлена"


class ReasonNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Причина не найдена"


class ReasonNotFoundException(ObjectNotFoundException):
    detail = "Причина не найдена"


class ReportNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Жалоба не найдена"


class ReportNotFoundException(ObjectNotFoundException):
    detail = "Жалоба не найдена"


class AlreadyBannedHTTPException(AlreadyExistsHTTPException):
    detail = "Этот пользователь уже забанен"


class AlreadyBannedException(AlreadyExistsException):
    detail = "Этот пользователь уже забанен"


class InvalidBanDateHTTPException(LumeHTTPException):
    detail = "Дата бана указана на прошедшую, либо сегодняшнюю дату"
    status_code = 422


class UserNotBannedHTTPException(ObjectNotFoundHTTPException):
    detail = "Пользователь, бан на которого вы пытаетесь снять, не забанен, либо не существует"


class UserNotBannedException(ObjectNotFoundException):
    detail = "Пользователь, бан на которого вы пытаетесь снять, не забанен, либо не существует"
