import logging

"""
Временный файл! Создан для проверки новых фич

Запустить этот файл отдельно:
pytest -s -v tests/unit/test_factory.py
"""
from tests.factories.books_factory import BookAddFactory


async def test_fixture(check_content_integration_tests):
    logging.info("ТЕСТ ФИКСТУРЫ")
