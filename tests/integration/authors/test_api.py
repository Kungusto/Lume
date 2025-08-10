import pytest
from tests.utils import ServiceForTests
from src.schemas.books import BookPATCHWithRels


"""
Выполнить тест отдельно:
pytest -s -v tests/integration/books/test_api.py::*название функции теста*
"""


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


async def test_add_book(auth_new_author):
    response_publicate = await auth_new_author.post(
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

    response_my_books = await auth_new_author.get(url="/author/my_books")
    assert response_my_books.status_code == 200


async def test_patch_book(db, authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book
    data_to_edit = {"genres": [1, 3], "age_limit": 16, "tags": ["тайна", "футуризм"]}
    response_edit = await author_client.patch(
        url=f"/author/book/{book.book_id}",
        json=data_to_edit,
    )
    book_in_db = await db.books.get_one(book_id=book.book_id)

    assert response_edit.status_code == 200
    assert book_in_db
    assert book_in_db.age_limit == data_to_edit.get("age_limit", None)


async def test_delete_book(authorized_client_with_new_book, db):
    author_client, book = authorized_client_with_new_book

    response_delete = await author_client.delete(url=f"/author/book/{book.book_id}")
    assert response_delete.status_code == 200
    assert not await db.books.get_filtered(book_id=book.book_id)


async def test_get_book(authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book

    response_get_this_book = await author_client.get(url=f"/books/{book.book_id}")
    api_book_json = response_get_this_book.json()

    assert response_get_this_book.status_code == 200
    assert api_book_json.get("book_id", "None") == book.book_id
    assert api_book_json.get("title", "None") == book.title
    assert api_book_json.get("age_limit", "None") == book.age_limit
    assert api_book_json.get("description", "None") == book.description


async def test_user_cannot_modify_or_create_books(auth_new_user, new_book):
    response_edit = await auth_new_user.patch(
        url=f"/author/book/{new_book.book_id}",
        json={"genres": [1, 3], "age_limit": 16, "tags": ["тайна", "футуризм"]},
    )
    assert response_edit.status_code == 403

    response_delete = await auth_new_user.delete(url=f"/author/book/{new_book.book_id}")
    assert response_delete.status_code == 403

    response_publicate_second = await auth_new_user.post(
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
        [BookPATCHWithRels(genres=[9999, 10000]), 404],
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
async def test_edit_book(patch_data, status_code, authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book
    data_to_update = patch_data.model_dump(exclude_unset=True)
    response_edit = await author_client.patch(
        url=f"/author/book/{book.book_id}", json=data_to_update
    )
    assert response_edit.status_code == status_code
    updated_book_response = await author_client.get(url=f"/books/{book.book_id}")
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


async def test_add_already_exist_content(
    authorized_client_with_new_book,
    check_content_for_tests,
    s3,
    db,
):
    author_client, book = authorized_client_with_new_book

    list_images = [f"books/{book.book_id}/images/page_0_img_0.png"]
    file_path = "books/content/test_book.pdf"
    file, filename = await ServiceForTests.get_file_and_name(file_path)

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


async def test_add_not_book(authorized_client_with_new_book, db, s3):
    author_client, book = authorized_client_with_new_book
    file_path = "books/content/not_a_book.jpg"
    file, filename = await ServiceForTests.get_file_and_name(file_path)
    list_images = []

    response_add_content = await author_client.post(
        url=f"/author/content/{book.book_id}", files={"file": (filename, file)}
    )
    all_images = await s3.books.list_objects_by_prefix(
        prefix=f"books/{book.book_id}/images"
    )
    assert response_add_content.status_code == 422
    book = await db.books.get_one(book_id=book.book_id)
    assert len(all_images) == len(list_images)
    assert all_images == list_images
    assert not book.is_rendered


@pytest.mark.parametrize(
    "book_path_in_local_file_system, images_count",
    [
        ["books/content/test_book.pdf", 1],
        ["books/content/test_book_2.pdf", 2],
    ],
)
async def test_add_already_exists_content(
    book_path_in_local_file_system: str,
    images_count: int,
    authorized_client_with_new_book,
    db,
    s3,
):
    author_client, book = authorized_client_with_new_book
    file, filename = await ServiceForTests.get_file_and_name(
        book_path_in_local_file_system
    )

    response_add_content = await author_client.post(
        url=f"/author/content/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_content.status_code == 200

    all_images = await s3.books.list_objects_by_prefix(
        prefix=f"books/{book.book_id}/images"
    )
    book = await db.books.get_one(book_id=book.book_id)
    assert len(all_images) == images_count
    assert book.is_rendered


@pytest.mark.parametrize(
    "cover_path_in_content_bucket, status_code",
    [
        ["books/covers/not_a_cover.pdf", 422],
        ["books/covers/not_tall_enough.jpg", 422],
        ["books/covers/normal_cover.jpg", 200],
    ],
)
async def test_add_cover(
    cover_path_in_content_bucket,
    status_code,
    authorized_client_with_new_book,
    check_content_for_tests,
    s3,
    db,
):
    author_client, book = authorized_client_with_new_book
    file, filename = await ServiceForTests.get_file_and_name(
        cover_path_in_content_bucket
    )
    response_add_cover = await author_client.post(
        url=f"author/cover/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_cover.status_code == status_code

    if status_code != 200:
        return

    book = await db.books.get_one(book_id=book.book_id)
    assert book.cover_link is not None
    assert await s3.books.check_file_by_path(f"books/{book.book_id}/preview.png")


async def test_add_already_exists_cover(authorized_client_with_new_book_with_cover):
    author_client, book = authorized_client_with_new_book_with_cover
    file, filename = await ServiceForTests.get_file_and_name(
        "books/covers/normal_cover.jpg"
    )
    response_add_cover = await author_client.post(
        url=f"author/cover/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_cover.status_code == 409


@pytest.mark.parametrize(
    "cover_path, status_code",
    [
        # ["books/covers/normal_cover.jpg", 404],
        ["books/covers/not_a_cover.pdf", 422],
        ["books/covers/not_tall_enough.jpg", 422],
        ["books/covers/normal_cover.jpg", 200],
    ],
)
async def test_edit_cover(
    cover_path,
    status_code,
    check_content_for_tests,
    authorized_client_with_new_book_with_cover,
    s3,
    db,
):
    author_client, book = authorized_client_with_new_book_with_cover
    file, filename = await ServiceForTests.get_file_and_name(cover_path)
    response_add_cover = await author_client.put(
        url=f"author/cover/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_cover.status_code == status_code

    if status_code != 200:
        return

    book = await db.books.get_one(book_id=book.book_id)
    assert book.cover_link is not None
    assert await s3.books.check_file_by_path(f"books/{book.book_id}/preview.png")


async def test_edit_book_without_cover(authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book
    file, filename = await ServiceForTests.get_file_and_name(
        "books/covers/normal_cover.jpg"
    )
    response_add_cover = await author_client.put(
        url=f"author/cover/{book.book_id}", files={"file": (filename, file)}
    )
    assert response_add_cover.status_code == 404


async def test_edit_non_existing_book(authorized_client_with_new_book):
    author_client, _ = authorized_client_with_new_book
    file, filename = await ServiceForTests.get_file_and_name(
        "books/covers/normal_cover.jpg"
    )
    response_add_cover = await author_client.put(
        url="author/cover/99999", files={"file": (filename, file)}
    )
    assert response_add_cover.status_code == 403


async def test_get_render_status(authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book
    response_get_status = await author_client.get(
        f"/author/{book.book_id}/publication_status"
    )
    assert response_get_status.status_code == 200
