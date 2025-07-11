import logging
import pytest
from src.utils.helpers import FileManager

"""
Временный файл! Создан для проверки новых фич

Запустить этот файл отдельно:
pytest -s -v tests/unit/test_factory.py
"""


# async def test_fixture(authorized_client_with_new_book):
#     logging.info("ТЕСТ ФИКСТУРЫ")


# @pytest.mark.parametrize(
#     "book_path_in_local_file_system, status_code, list_images, book_id",
#     [
# ✅      ["books/content/test_book.pdf", 200, ["books/1/images/page_0_img_0.png"], 1],
# ❌       ["books/content/test_book.pdf", 409, None, 1],
# ❌        ["books/content/not_a_book.jpg", 422, None, 2],
# ❌       [
#             "books/content/test_book_2.pdf",  # book_path_in_local_file_system
#             200,  # status_code
#             ["books/2/images/page_1_img_0.png", "books/2/images/page_1_img_1.png"],
#             2,  # book_id
#         ],
#     ],
# )
async def test_add_content(
    # book_path_in_local_file_system,
    # status_code,
    # list_images,
    # book_id,
    authorized_client_with_new_book,
    check_content_integration_tests,
    s3,
    db,
):
    author_client, book = authorized_client_with_new_book

    list_images = ["books/1/images/page_0_img_0.png"]
    file_path = "books/content/test_book.pdf"
    file = await FileManager().get_file_by_rel_path(file_path)
    filename = file_path.split("/")[-1]  #  = test_book.pdf

    response_add_content = await author_client.post(
        url=f"/author/content/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_content.status_code == 200

    all_images = await s3.books.list_objects_by_prefix(
        prefix=f"books/{book.book_id}/images"
    )
    book = await db.books.get_one(book_id=book.book_id)
    assert len(all_images) == len(list_images)
    assert all_images == list_images
    assert book.is_rendered

    # добавляем контент к книге, у которой он уже есть
    response_add_content_again = await author_client.post(
        url=f"/author/content/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_content_again.status_code == 409