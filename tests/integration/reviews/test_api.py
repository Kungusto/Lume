"""
Выполнить эти тесты отдельно:
pytest -s -v tests/integration/reviews/test_api.py
"""


async def test_add_review(auth_ac_user, db):
    # публикуем отзыв на несуществующую книгу
    response_add = await auth_ac_user.post(
        url="/reviews/by_book/9999",
        json={"rating": 5, "text": "Хорошая книга! Жаль что ее не существует"},
    )
    assert response_add.status_code == 404

    # добавляем подходящий по всем критериям отзыв
    response_add = await auth_ac_user.post(
        url="/reviews/by_book/1", json={"rating": 4, "text": "Хорошая книга!"}
    )
    assert response_add.status_code == 200

    # Пробуем добавить еще один отзыв
    response_add = await auth_ac_user.post(
        url="/reviews/by_book/1",
        json={"rating": 4, "text": "Второй отзыв на ту же самую книгу!"},
    )
    assert response_add.status_code == 409


async def test_edit_reviews(ac, db):
    # логинимся как один из "замоканных" пользователей
    response_login = await ac.post(
        url="auth/login",
        json={"email": "alice@example.com", "password": "hashed_pass_123"},
    )
    assert response_login.status_code == 200

    # пробуем изменить чужой отзыв
    response_edit_alien_review = await ac.put(
        url="/reviews/1", json={"rating": 5, "text": "Ха-ха-ха, этот отзыв не мой!"}
    )
    assert response_edit_alien_review.status_code == 403

    # пробуем изменить свой отзыв
    response_edit_my_review = await ac.put(
        url="/reviews/2",
        json={"rating": 5, "text": "Очень интересная книга с интересным финалом!"},
    )
    assert response_edit_my_review.status_code == 200

    # пробуем изменить несуществующий отзыв
    response_edit_my_review = await ac.put(
        url="/reviews/9999",
        json={"rating": 5, "text": "этого отзыва не существует:)"},
    )
    assert response_edit_my_review.status_code == 404

    ac.cookies.clear()


async def test_delete_reviews(ac, db):
    # логинимся как один из "замоканных" пользователей
    response_login = await ac.post(
        url="auth/login",
        json={"email": "alice@example.com", "password": "hashed_pass_123"},
    )
    assert response_login.status_code == 200

    # проверяем, существует ли нужный нам отзыв
    review = await db.reviews.get_filtered(review_id=7)
    assert review

    # пробуем удалить чужой отзыв
    response_delete_alien_review = await ac.delete(url="reviews/1")
    assert response_delete_alien_review.status_code == 403

    # пробуем удалить несуществующий отзыв
    response_edit_my_review = await ac.delete(
        url="/reviews/9999",
    )
    assert response_edit_my_review.status_code == 404

    # пробуем удалить свой отзыв
    response_edit_my_review = await ac.delete(
        url="/reviews/7",
    )
    assert response_edit_my_review.status_code == 200

    # проверяем, удалился ли отзыв
    review = await db.reviews.get_filtered(review_id=7)
    assert not review

    ac.cookies.clear()


async def test_get_my_reviews(ac, db):
    ac.cookies.clear()
    response_login = await ac.post(
        url="auth/login",
        json={"email": "bob@example.com", "password": "hashed_pass_456"},
    )

    assert response_login.status_code == 200

    # получаем из бд все свои отзывы, для будущей проверки
    my_reviews = await db.reviews.get_filtered(user_id=2)

    # получаем все свои отзывы
    response_get_my_reviews = await ac.get(url="reviews/my_reviews")
    my_reviews_json = response_get_my_reviews.json()

    assert response_get_my_reviews.status_code == 200
    assert len(my_reviews_json) == len(my_reviews)


async def test_get_book_reviews(ac, db):
    book_reviews_in_db = await db.reviews.get_filtered(book_id=1)
    book_reviews_reponse = await ac.get(url="reviews/by_book/1")
    book_reviews_json = book_reviews_reponse.json()
    assert book_reviews_reponse.status_code == 200
    assert len(book_reviews_json) == len(book_reviews_in_db)


async def test_check_rate_yourself(auth_ac_author):
    response_add = await auth_ac_author.post(
        url="/reviews/by_book/1",
        json={"rating": 5, "text": "Я оцениваю свою же книгу!"},
    )
    assert response_add.status_code == 403


async def test_admin_edit_alian_reviews(auth_ac_admin, db):
    response_add_as_admin = await auth_ac_admin.post(
        url="/reviews/by_book/1",
        json={"rating": 5, "text": "Я оцениваю книгу как админ!"},
    )
    response_add_as_admin.status_code == 200

    response_add_as_admin_again = await auth_ac_admin.post(
        url="/reviews/by_book/1",
        json={"rating": 5, "text": "Я оцениваю книгу дважды как админ!"},
    )
    response_add_as_admin_again.status_code == 200

    data_to_edit = {"rating": 1, "text": "Этот отзыв изменил сам админ!"}
    reponse_edit_alien_review_as_admin = await auth_ac_admin.put(
        url="/reviews/1", json=data_to_edit
    )
    reponse_edit_alien_review_as_admin.status_code == 200
    edited_review_in_db = await db.reviews.get_one(review_id=1)
    assert edited_review_in_db.rating == data_to_edit.get("rating", None)
    assert edited_review_in_db.text == data_to_edit.get("text", None)

    response_delete_as_admin = await auth_ac_admin.delete(url="/reviews/1")
    response_delete_as_admin.status_code == 200
    deleted_review_in_db = await db.reviews.get_filtered(review_id=1)
    assert not deleted_review_in_db
