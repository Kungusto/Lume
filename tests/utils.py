from pathlib import Path
from src.exceptions.conftest import MissingFilesException, MissingTestDataException


class ServiceForTests:
    """Позже тут появятся полезные функции для удобочитаемости тестов"""

    @staticmethod
    def check_necessarily_files(folder_path: str, need_files: set[str]):
        try:
            existing_files = {f.name for f in Path(folder_path).iterdir() if f.is_file()}
        except FileNotFoundError as ex:
            raise MissingTestDataException(folder_path=folder_path) from ex
        if not need_files.issubset(existing_files):
            sets_difference = list(need_files - existing_files)
            raise MissingFilesException(
                missing_files=sets_difference, folder_path=folder_path
            )
