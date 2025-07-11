from pathlib import Path
from src.exceptions.conftest import (
    MissingFilesException,
    DirectoryNotFoundException,
    DirectoryIsEmptyException,
)
from src.utils.helpers import FileManager


class ServiceForTests:
    """Класс с методами проверки наличия и содержимого директорий, используемых в тестах"""

    @staticmethod
    def check_required_files(folder_path: str, need_files: set[str]):
        existing_files = FileManager.get_list_files_by_folder_path(
            folder_path=folder_path
        )
        if not need_files.issubset(existing_files):
            sets_difference = list(need_files - existing_files)
            raise MissingFilesException(
                missing_files=sets_difference, folder_path=folder_path
            )

    @staticmethod
    def check_not_empty(folder_path: str):
        existing_files = FileManager.get_list_files_by_folder_path(
            folder_path=folder_path
        )
        if not existing_files:
            raise DirectoryIsEmptyException(folder_path=folder_path)
