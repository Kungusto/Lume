import logging

"""
Временный файл! Создан для проверки работоспособности фабрик

Запустить этот файл отдельно:
pytest -s -v tests/unit/test_factory.py
"""
from tests.factories.books_factory import BookAddFactory


async def test_factory_book(new_book):
    logging.info("ТЕСТ ФИКСТУРЫ")
