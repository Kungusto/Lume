from src.exceptions.base import (
    FileValidationHTTPException,
    FileValidationException,
    ObjectNotFoundException,
    ObjectNotFoundHTTPException,
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
    def __init__(self, file_path: str = "", *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        if not file_path:
            self.detail = "Файл не найден"
        else:
            self.detail = f"Файл {file_path} не найден"


class StatementNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Автоматический отчет еще не сгенерирован"


class StatementNotFoundException(ObjectNotFoundException):
    detail = "Автоматический отчет еще не сгенерирован"
