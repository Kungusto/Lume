from src.exceptions.base import (
    AlreadyExistsException,
    ObjectNotFoundHTTPException,
    ObjectNotFoundException,
    PasswordValidationException,
    AuthentificationException,
    AlreadyExistsHTTPException,
    AuthentificationHTTPException,
)

# =---=---=---=---=---= Base Exceptions =---=---=---=---=---= #


# Ошибки валидации пароля
class TooLongPasswordException(PasswordValidationException):
    detail = "Пароль должен быть длинее, чем 50 символов"


class TooShortPasswordException(PasswordValidationException):
    detail = "Пароль должен быть короче, чем 5 символов"


# Ошибки с логином и регистрацией
class NotAuthentificatedException(AuthentificationException):
    detail = "Вы не аутентифицированы"


class AlreadyAuthentificatedException(AuthentificationException):
    detail = "Вы уже аутентифицированы"


class WrongPasswordOrEmailException(AuthentificationException):
    detail = "Неправильная пароль, либо почта"


class ExpireTokenException(AuthentificationException):
    detail = "Срок действия токена истек"


# Объект уже есть в бд
class EmailAlreadyRegistratedException(AlreadyExistsException):
    detail = "Пользователь с таким email уже существует"


class NickAlreadyRegistratedException(AlreadyExistsException):
    detail = "Это имя пользователя уже занято"


# Нету объекта в бд
class EmailNotFoundException(ObjectNotFoundException):
    detail = "Почта не найдена"


class UserNotFoundException(ObjectNotFoundException):
    detail = "Пользователь не найден"


# =---=---=---=---=---= HTTP Exceptions =---=---=---=---=---= #


# Объект уже есть в бд
class EmailAlreadyRegistratedHTTPException(AlreadyExistsHTTPException):
    detail = "Пользователь с таким email уже существует"


class NickAlreadyRegistratedHTTPException(AlreadyExistsHTTPException):
    detail = "Это имя пользователя уже занято"


class AlreadyAuthentificatedHTTPException(AlreadyExistsHTTPException):
    detail = "Вы уже аутентифицированы"


# Ошибка аутентификации
class TooLongPasswordHTTPException(AuthentificationHTTPException):
    detail = "Пароль должен быть длинее, чем 50 символов"


class TooShortPasswordHTTPException(AuthentificationHTTPException):
    detail = "Пароль должен быть короче, чем 5 символов"


class WrongPasswordOrEmailHTTPException(AuthentificationHTTPException):
    detail = "Неправильный пароль, либо почта"


class NotAuthentificatedHTTPException(AuthentificationHTTPException):
    detail = "Вы не аутентифицированы"


class ExpireTokenHTTPException(AuthentificationHTTPException):
    detail = "Срок действия токена истек"


# Объекта не существует
class UserNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Пользователь не найден"


class EmailNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Почта не найдена"
