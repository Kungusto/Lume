from src.exceptions.base import ObjectNotFoundException, LumeException

# -- Исключения в фикстурах тестов


class DirectoryNotFoundException(ObjectNotFoundException):
    def __init__(self, folder_path: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.detail = f"Не найдена обязательная директория: {folder_path}"


class MissingFilesException(ObjectNotFoundException):
    def __init__(self, missing_files: list[str], folder_path, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.detail = f"Не найдены некоторые обязательные файлы в папке {folder_path}: {missing_files}"


class DirectoryIsEmptyException(ObjectNotFoundException):
    def __init__(self, folder_path: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.detail = f"Папка {folder_path} существует, но пуста"


class ReadFileException(LumeException):
    def __init__(self, filename: str, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.detail = f"Ошибка чтения файла: {filename}"