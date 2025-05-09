from fastapi import HTTPException


class LumeException(Exception):
    detail = "Непредвиденная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


# --- Object not found
class ObjectNotFoundException(LumeException):
    detail = "Сущность не найдена"


class UserNotFoundException(LumeException):
    detail = "Пользователь не найден"


class EmailNotFoundException(LumeException):
    detail = "Почта не найдена"


class BookNotFoundException(LumeException):
    detail = "Книга не найдена"


# ---


class EmailAlreadyRegistratedException(LumeException):
    detail = "Пользователь с таким email уже существует"


class NickAlreadyRegistratedException(LumeException):
    detail = "Это имя пользователя уже занято"


class TooLongPasswordException(LumeException):
    detail = "Пароль должен быть длинее, чем 50 символов"


class TooShortPasswordException(LumeException):
    detail = "Пароль должен быть короче, чем 5 символов"


class NotAuthentificatedException(LumeException):
    detail = "Вы не аутентифицированы"


class AlreadyAuthentificatedException(LumeException):
    detail = "Вы уже аутентифицированы"


class ExpireTokenException(LumeException):
    detail = "Срок действия токена истек"


class WrongPasswordOrEmailException(LumeException):
    detail = "Неправильная пароль, либо почта"


# ------------------------------------ HTTP Exceptions ------------------------------------


class LumeHTTPException(HTTPException):
    detail = None
    status_code = 400

    def __init__(self):
        super().__init__(detail=self.detail, status_code=self.status_code)


class EmailAlreadyRegistratedHTTPException(LumeHTTPException):
    detail = "Пользователь с таким email уже существует"


class NickAlreadyRegistratedHTTPException(LumeHTTPException):
    detail = "Это имя пользователя уже занято"


class TooLongPasswordHTTPException(LumeHTTPException):
    detail = "Пароль должен быть длинее, чем 50 символов"


class TooShortPasswordHTTPException(LumeHTTPException):
    detail = "Пароль должен быть короче, чем 5 символов"


class InternalServerErrorHTTPException(LumeHTTPException):
    detail = "Непредвиденная ошибка на стороне сервера"
    status_code = 500


class NotAuthentificatedHTTPException(LumeHTTPException):
    detail = "Вы не аутентифицированы"
    status_code = 401


class AlreadyAuthentificatedHTTPException(LumeHTTPException):
    detail = "Вы уже аутентифицированы"


class ExpireTokenHTTPException(LumeHTTPException):
    detail = "Срок действия токена истек"
    status_code = 401


# --- Object not found ---
class ObjectNotFoundHTTPException(LumeHTTPException):
    detail = "Сущность не найдена"
    status_code = 404


class UserNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Пользователь не найден"


class CoverNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "К этой книге пока нету обложек"


class BookNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Книга не найдена"


# --- Permission Denied ---
class PermissionDeniedHTTPException(LumeHTTPException):
    detail = "Недостаточно прав для совершения данной операции"


class WrongPasswordOrEmailHTTPException(LumeHTTPException):
    detail = "Неправильная пароль, либо почта"


class BookNotExistsOrYouNotOwnerHTTPException(LumeHTTPException):
    detail = "Книга не существует, либо у вас нет доступа к ее изменению"


class ContentAlreadyExistsHTTPException(LumeHTTPException):
    detail = "Контент книги уже был опубликован"
