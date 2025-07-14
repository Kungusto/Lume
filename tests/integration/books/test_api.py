import pytest


@pytest.mark.parametrize(
    "params, status_code",
    [
        [{"page": 1, "per_page": 5, "max_age": 1, "min_age": 2}, 400],
        [
            {
                "page": 1,
                "per_page": 5,
                "later_than": "2030-01-02",
                "earlier_than": "2000-01-01",
            },
            400,
        ],
        [{"page": 1, "per_page": 5, "min_rating": 5, "max_rating": 1}, 400],
        [{"page": 1, "per_page": 5, "min_readers": 5, "max_readers": 1}, 400],
        [{"page": 1, "per_page": 5}, 200],
    ],
)
async def test_get_with_pagination(ac, params, status_code, new_publicated_book, db):
    response_search = await ac.get("/books", params=params)
    assert response_search.status_code == status_code
    if status_code != 200:
        return
    # проверяем, не пустой ли ответ
    assert response_search.json()


async def test_get_book_with_cover(ac, new_publicated_book_with_cover):
    response_search = await ac.get(
        "/books",
        params={
            "page": 1,
            "per_page": 10,
            "book_title": new_publicated_book_with_cover.title,
        },
    )
    assert response_search.status_code == 200


async def test_get_all_genres(ac, seed_genres):
    response = await ac.get("/books/genres")
    assert response.status_code == 200
    assert response.json()


async def test_download_book(ac2, authorized_client_new_book_with_content):
    _, book = authorized_client_new_book_with_content
    response_download_book = await ac2.get(f"books/download/{book.book_id}")
    assert response_download_book.status_code == 200
    assert response_download_book.json()

    response_download_book = await ac2.get("books/download/99999")
    assert response_download_book.status_code == 404


async def test_download_book_without_content(ac, new_book):
    response_download_book = await ac.get(f"books/download/{new_book.book_id}")
    assert response_download_book.status_code == 404


async def test_get_book_with_rels(ac, new_book):
    response_get_book = await ac.get(f"books/{new_book.book_id}")
    assert response_get_book.status_code == 200

    response_get_non_exist_book = await ac.get("books/9999")
    assert response_get_non_exist_book.status_code == 404


async def test_get_book_page(
    auth_new_second_user, authorized_client_new_book_with_content
):
    # (контент взят из локального books/content/test_book_2.pdf)
    _, book = authorized_client_new_book_with_content

    # получаем первую страницу, на которой нет изображений
    response_get_page = await auth_new_second_user.get(f"books/{book.book_id}/page/1")
    assert response_get_page.status_code == 200
    assert response_get_page.json()

    # получаем вторую страницу, на которой есть два изображения
    response_get_page = await auth_new_second_user.get(f"books/{book.book_id}/page/2")
    assert response_get_page.status_code == 200
    assert response_get_page.json()

    # пытаемся получить несуществующую страницу
    response_get_page = await auth_new_second_user.get(
        f"books/{book.book_id}/page/4999"
    )
    assert response_get_page.status_code == 404
    assert response_get_page.json()

    # пытаемся получить страницу несуществующей книги
    response_get_page = await auth_new_second_user.get("books/9999/page/1")
    assert response_get_page.status_code == 404
    assert response_get_page.json()


async def test_get_page_from_book_without_content(new_book, auth_new_second_user):
    response_get_page = await auth_new_second_user.get(
        f"books/{new_book.book_id}/page/1"
    )
    assert response_get_page.status_code == 404
    assert response_get_page.json()


async def test_report_book(new_book, auth_new_user, new_reason):
    # Корректные данные - 200 OK
    response_add_report = await auth_new_user.post(
        url=f"books/{new_book.book_id}/report",
        json={"reason_id": new_reason.reason_id, "comment": "Это плагиат!"},
    )
    assert response_add_report.status_code == 200
    assert response_add_report.json()

    # Пытаемся пожаловаться на несуществующую книгу
    response_add_report = await auth_new_user.post(
        url="books/9999/report",
        json={
            "reason_id": new_reason.reason_id,
            "comment": "Жалуюсь не несуществующую книгу",
        },
    )

    # Пытаемся пожаловаться по несуществующей причине
    assert response_add_report.status_code == 404
    assert response_add_report.json()
    response_add_report = await auth_new_user.post(
        url=f"books/{new_book.book_id}/report",
        json={"reason_id": 9999, "comment": "Жалуюсь по вымышленной причине"},
    )
    assert response_add_report.status_code == 404
    assert response_add_report.json()
