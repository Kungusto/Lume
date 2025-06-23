async def test_registration_as_author(ac):
    response = await ac.post(
        url="/auth/register",
        json={
            "role": "AUTHOR",
            "email": "john.doe@example.com",
            "name": "John",
            "surname": "Doe",
            "nickname": "johnd",
            "password": "SecureP@ssw0rd123"
        }
    )
    assert response.status_code == 200


async def test_base_crud_books(ac, redis, ping_taskiq): 
    response_login = await ac.post(
        url="auth/login",
        json={
            "email": "david.writer@example.com",
            "password": "hashed_pass_321"
        }
    )

    assert response_login.status_code == 200

    response_publicate = await ac.post(
        url="/author/book",
        json={
            "title": "Тайны времени",
            "age_limit": 16,
            "description": "Захватывающее путешествие сквозь время, где ничто не является тем, чем кажется.",
            "language": "Russian",
            "authors": [], 
            "genres": [1],
            "tags": ["путешествия во времени", "тайна", "приключения"]
        }
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
            "tags": ["антиутопия", "память", "будущее", "тайна"]
        }
    )
    second_book_id = response_publicate_second.json()["data"]["book_id"]
    assert response_publicate_second.status_code == 200


    response_edit = await ac.patch(
        url=f"/author/book?book_id={second_book_id}",
        json={
            "genres": [1, 3],
            "age_limit": 16,
            "tags": ["тайна", "футуризм"]
        }
    )
    assert response_edit.status_code == 200


    response_my_books = await ac.get(
        url="/author/my_books"
    )
    books = response_my_books.json()[0]["books"]
    assert response_my_books.status_code == 200
    assert books[0]["title"] == "Тайны времени"
    
    second_book = books[1]
    assert second_book["title"] == "Город без памяти"
    assert sorted([genre["genre_id"] for genre in second_book["genres"]]) == [1, 3]
    assert second_book["age_limit"] == 16
    assert sorted([tag["title_tag"] for tag in second_book["tags"]]) == ["тайна", "футуризм"]
    assert isinstance(books, list)
    for book in books: 
        assert isinstance(book, dict)

    
    response_delete = await ac.delete(
        url=f"/author/book?book_id={second_book_id}"
    )
    assert response_delete.status_code == 200

    response_get_this_book = await ac.get(
        url=f"/author/book?book_id={second_book_id}"
    )
    assert response_get_this_book.status_code == 404

    ac.cookies.clear()


