"""
Выполнить эти тесты отдельно:
pytest -s -v tests/integration/reviews/test_api.py
"""


async def test_add_review(auth_new_user, new_book):
    # публикуем отзыв на несуществующую книгу
    response_add = await auth_new_user.post(
        url="/reviews/by_book/9999",
        json={"rating": 5, "text": "Хорошая книга! Жаль что ее не существует"},
    )
    assert response_add.status_code == 404

    # добавляем подходящий по всем критериям отзыв
    response_add = await auth_new_user.post(
        url=f"/reviews/by_book/{new_book.book_id}",
        json={"rating": 4, "text": "Хорошая книга!"},
    )
    assert response_add.status_code == 200

    # Пробуем добавить еще один отзыв
    response_add = await auth_new_user.post(
        url=f"/reviews/by_book/{new_book.book_id}",
        json={"rating": 4, "text": "Второй отзыв на ту же самую книгу!"},
    )
    assert response_add.status_code == 409


async def test_edit_my_reviews(new_review_with_author_ac):
    author_client, review = new_review_with_author_ac

    # пробуем изменить свой отзыв
    response_edit_my_review = await author_client.put(
        url=f"/reviews/{review.review_id}",
        json={"rating": 5, "text": "Очень интересная книга с интересным финалом!"},
    )
    assert response_edit_my_review.status_code == 200

    # пробуем изменить несуществующий отзыв
    response_edit_my_review = await author_client.put(
        url="/reviews/9999",
        json={"rating": 5, "text": "этого отзыва не существует:)"},
    )
    assert response_edit_my_review.status_code == 404


async def test_edit_alien_reviews(auth_new_second_user, new_review):
    # пробуем изменить чужой отзыв
    response_edit_alien_review = await auth_new_second_user.put(
        url=f"/reviews/{new_review.review_id}",
        json={"rating": 5, "text": "Ха-ха-ха, этот отзыв не мой!"},
    )
    assert response_edit_alien_review.status_code == 403


async def test_delete_reviews(auth_new_second_user, new_review_with_author_ac, db):
    author_client, review = new_review_with_author_ac
    # проверяем, существует ли нужный нам отзыв
    review_in_db = await db.reviews.get_filtered(review_id=review.review_id)
    assert review_in_db

    # пробуем удалить чужой отзыв
    response_delete_alien_review = await auth_new_second_user.delete(
        url=f"reviews/{review.review_id}"
    )
    assert response_delete_alien_review.status_code == 403

    # пробуем удалить несуществующий отзыв
    response_edit_my_review = await auth_new_second_user.delete(
        url="/reviews/9999",
    )
    assert response_edit_my_review.status_code == 404

    # пробуем удалить свой отзыв
    response_edit_my_review = await author_client.delete(
        url=f"/reviews/{review.review_id}",
    )
    assert response_edit_my_review.status_code == 200

    # проверяем, удалился ли отзыв
    review = await db.reviews.get_filtered(review_id=review.review_id)
    assert not review


async def test_get_my_reviews(db, new_review_with_author_ac):
    author_client, review = new_review_with_author_ac

    # получаем из бд все свои отзывы, для будущей проверки
    my_reviews = await db.reviews.get_filtered(user_id=review.user_id)

    # получаем все свои отзывы
    response_get_my_reviews = await author_client.get(url="reviews/my_reviews")
    my_reviews_json = response_get_my_reviews.json()

    assert response_get_my_reviews.status_code == 200
    assert len(my_reviews_json) == len(my_reviews)


async def test_get_book_reviews(ac, db, new_review):
    book_reviews_in_db = await db.reviews.get_filtered(book_id=new_review.book_id)
    book_reviews_reponse = await ac.get(url=f"reviews/by_book/{new_review.book_id}")
    book_reviews_json = book_reviews_reponse.json()
    assert book_reviews_reponse.status_code == 200
    assert len(book_reviews_json) == len(book_reviews_in_db)


async def test_check_rate_yourself(authorized_client_with_new_book):
    author_client, book = authorized_client_with_new_book
    response_add = await author_client.post(
        url=f"/reviews/by_book/{book.book_id}",
        json={"rating": 5, "text": "Я оцениваю свою же книгу!"},
    )
    assert response_add.status_code == 403


async def test_admin_edit_alian_reviews(auth_new_admin, new_review, db):
    response_add_as_admin = await auth_new_admin.post(
        url=f"/reviews/by_book/{new_review.review_id}",
        json={"rating": 5, "text": "Я оцениваю книгу как админ!"},
    )
    assert response_add_as_admin.status_code == 200

    response_add_as_admin_again = await auth_new_admin.post(
        url=f"/reviews/by_book/{new_review.review_id}",
        json={"rating": 5, "text": "Я оцениваю книгу дважды как админ!"},
    )
    assert response_add_as_admin_again.status_code == 200

    data_to_edit = {"rating": 1, "text": "Этот отзыв изменил сам админ!"}
    reponse_edit_alien_review_as_admin = await auth_new_admin.put(
        url=f"/reviews/{new_review.review_id}", json=data_to_edit
    )
    assert reponse_edit_alien_review_as_admin.status_code == 200
    edited_review_in_db = await db.reviews.get_one(review_id=new_review.review_id)
    assert edited_review_in_db.rating == data_to_edit.get("rating", None)
    assert edited_review_in_db.text == data_to_edit.get("text", None)

    response_delete_as_admin = await auth_new_admin.delete(
        url=f"/reviews/{new_review.review_id}"
    )
    assert response_delete_as_admin.status_code == 200
    deleted_review_in_db = await db.reviews.get_filtered(review_id=new_review.review_id)
    assert not deleted_review_in_db
