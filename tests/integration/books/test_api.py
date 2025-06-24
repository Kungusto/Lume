import pytest
from src.schemas.books import BookPATCHWithRels


async def test_registration_as_author(ac):
    response = await ac.post(
        url="/auth/register",
        json={
            "role": "AUTHOR",
            "email": "john.doe@example.com",
            "name": "John",
            "surname": "Doe",
            "nickname": "johnd",
            "password": "SecureP@ssw0rd123",
        },
    )
    assert response.status_code == 200


async def test_base_crud_books(ac, redis, ping_taskiq):
    ac.cookies.clear()

    response_login_author = await ac.post(
        url="auth/login",
        json={"email": "david.writer@example.com", "password": "hashed_pass_321"},
    )
    assert response_login_author.status_code == 200

    response_publicate = await ac.post(
        url="/author/book",
        json={
            "title": "Тайны времени",
            "age_limit": 16,
            "description": "Захватывающее путешествие сквозь время, где ничто не является тем, чем кажется.",
            "language": "Russian",
            "authors": [],
            "genres": [1],
            "tags": ["путешествия во времени", "тайна", "приключения"],
        },
    )
    assert response_publicate.status_code == 200

    response_publicate_second = await ac.post(
        url="/author/book",
        json={
            "title": "Город без памяти",
            "age_limit": 18,
            "description": "В мегаполисе, где каждый день начинается с чистого листа, один человек пытается вспомнить правду.",
            "language": "Russian",
            "authors": [],
            "genres": [2],
            "tags": ["антиутопия", "память", "будущее", "тайна"],
        },
    )
    second_book_id = response_publicate_second.json()["data"]["book_id"]
    assert response_publicate_second.status_code == 200

    response_edit = await ac.patch(
        url=f"/author/book?book_id={second_book_id}",
        json={"genres": [1, 3], "age_limit": 16, "tags": ["тайна", "футуризм"]},
    )
    assert response_edit.status_code == 200

    response_my_books = await ac.get(url="/author/my_books")
    assert response_my_books.status_code == 200

    response_delete = await ac.delete(url=f"/author/book?book_id={second_book_id}")
    assert response_delete.status_code == 200

    response_get_this_book = await ac.get(url=f"/author/book?book_id={second_book_id}")
    assert response_get_this_book.status_code == 404

    # чистим куки, имитируя разлогин пользователя
    ac.cookies.clear()

    response_login_user = await ac.post(
        url="/auth/login",
        json={"email": "carol@example.com", "password": "hashed_pass_789"},
    )
    assert response_login_user.status_code == 200
    assert "access_token" in ac.cookies.keys()

    response_edit = await ac.patch(
        url=f"/author/book?book_id={second_book_id}",
        json={"genres": [1, 3], "age_limit": 16, "tags": ["тайна", "футуризм"]},
    )
    assert response_edit.status_code == 403

    response_delete = await ac.delete(url=f"/author/book?book_id={second_book_id}")
    assert response_delete.status_code == 403

    response_publicate_second = await ac.post(
        url="/author/book",
        json={
            "title": "Город без памяти",
            "age_limit": 18,
            "description": "В мегаполисе, где каждый день начинается с чистого листа, один человек пытается вспомнить правду.",
            "language": "Russian",
            "authors": [],
            "genres": [2],
            "tags": ["антиутопия", "память", "будущее", "тайна"],
        },
    )
    assert response_publicate_second.status_code == 403

    ac.cookies.clear()


@pytest.mark.parametrize(
    "patch_data, status_code",
    [
        [BookPATCHWithRels(title="Артефакт"), 200],
        [BookPATCHWithRels(age_limit=18), 200],
        [BookPATCHWithRels(description="Очень интересная книга про артефакт"), 200],
        # -- Теги
        [BookPATCHWithRels(tags=["мистика", "артефакты", "реликвии"]), 200],
        [BookPATCHWithRels(tags=[f"тег{i}" for i in range(100)]), 200],
        [BookPATCHWithRels(tags=["МИСТИКА", "АРТЕФАКТЫ", "ДРЕВНОСТИ"]), 200],
        [BookPATCHWithRels(tags=[]), 200],
        # -- Жанры
        [BookPATCHWithRels(genres=[1, 2]), 200],
        [BookPATCHWithRels(genres=[2]), 200],
        [BookPATCHWithRels(genres=[1]), 200],
        [BookPATCHWithRels(genres=[]), 200],
        # -- Полное изменение
        [
            BookPATCHWithRels(
                title="Новая эпоха",
                age_limit=16,
                description="Полное обновление книги",
                genres=[1, 2],
                tags=["магия", "технологии"],
            ),
            200,
        ],
    ],
)
async def test_edit_book(patch_data, status_code, auth_ac_author):
    data_to_update = patch_data.model_dump(exclude_unset=True)
    response_edit = await auth_ac_author.patch(
        url="/author/book?book_id=1", json=data_to_update
    )
    assert response_edit.status_code == status_code
    updated_book_response = await auth_ac_author.get(url="/author/book?book_id=1")
    assert updated_book_response.status_code == 200
    if status_code != 200:
        return
    book = updated_book_response.json()

    # сравниваем значения двух словарей
    for key, value in data_to_update.items():
        if key == "genres":
            assert sorted([genre["genre_id"] for genre in book["genres"]]) == sorted(
                data_to_update["genres"]
            )
            continue
        if key == "tags":
            assert sorted([tag["title_tag"] for tag in book["tags"]]) == sorted(
                [tag.lower() for tag in data_to_update["tags"] or []]
            )
            continue
        assert book[key] == value


async def test_add_content(auth_ac_author, check_content_integration_tests, s3):
    file = await s3.books.get_file_by_path(
        is_content_bucket=True, s3_path="books/test_book.pdf"
    )
    response_add_content = await auth_ac_author.post(
        url="/author/content?book_id=1", files={"file": ("book.pdf", file)}
    )

    assert response_add_content.status_code == 200
