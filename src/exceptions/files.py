from src.exceptions.base import (
    FileValidationHTTPException,
    FileValidationException,
    ObjectNotFoundException,
)


class WrongFileExpensionException(FileValidationException):
    detail = "Данное расширение файла не поддерживается"


class WrongFileExpensionHTTPException(FileValidationHTTPException):
    detail = "Данное расширение файла не поддерживается"


class WrongCoverResolutionException(FileValidationException):
    detail = "Данное разрешение обложки не поддерживается"


class WrongCoverResolutionHTTPException(FileValidationHTTPException):
    detail = "Данное разрешение обложки не поддерживается"


class FileNotFoundException(ObjectNotFoundException):
    detail = "Файл не найден"
