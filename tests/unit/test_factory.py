from tests.utils import FileManager
"""
Временный файл! Создан для проверки новых фич

Запустить этот файл отдельно:
pytest -s -v tests/unit/test_factory.py
"""


async def test_new_method_in_file_manager():
    files = await FileManager().get_files_in_folder("other")
    print(files)