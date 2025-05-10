from fastapi import HTTPException


class LumeException(Exception):
    detail = "Непредвиденная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


# === Базовые исключения ===
class ObjectNotFoundException(LumeException):
    detail = "Сущность не найдена"


class AlreadyExistsException(LumeException):
    detail = "Объект уже существует"


class PasswordValidationException(LumeException):
    detail = "Ошибка валидации пароля"


class AuthentificationException(LumeException):
    detail = "Ошибка аутентификации"


# ------------------------------------ HTTP Exceptions ------------------------------------


class LumeHTTPException(HTTPException):
    detail = "Произошла непредвиденная ошибка"
    status_code = 400

    def __init__(self):
        super().__init__(detail=self.detail, status_code=self.status_code)


class InternalServerErrorHTTPException(LumeHTTPException):
    detail = "Непредвиденная ошибка на стороне сервера"
    status_code = 500


class AlreadyExistsHTTPException(LumeHTTPException):
    detail = "Объект уже существует"


class AuthentificationHTTPException(LumeHTTPException):
    detail = "Ошибка аутентификации"


class PasswordValidationHTTPException(LumeHTTPException):
    detail = "Ошибка валидации пароля"


class ObjectNotFoundHTTPException(LumeHTTPException):
    detail = "Сущность не найдена"
    status_code = 404


class PermissionDeniedHTTPException(LumeHTTPException):
    detail = "Недостаточно прав для совершения данной операции"
