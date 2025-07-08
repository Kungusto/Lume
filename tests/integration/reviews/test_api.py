"""
Выполнить тест отдельно:
pytest -s -v tests/integration/reviews/test_api.py
"""


async def test_add_review(auth_ac_user, db): 
    response_add = await auth_ac_user.post(
        url="/reviews/by_book/1",
        json={
            "rating": 4,
            "text": "Хорошая книга!"
        }
    )
    assert response_add.status_code == 200


async def test_edit_reviews(ac, db):
    response_login = await ac.post(
        url="auth/login",
        json={
            "email": "alice@example.com",
            "password": "hashed_pass_123"
        }
    )
    assert response_login.status_code == 200

    # пробуем изменить чужой отзыв
    response_edit_alien_review = await ac.put(
        url="/reviews/1",
        json={
            "rating": 5,
            "text": "Ха-ха-ха, этот отзыв не мой!"
        }
    )
    response_edit_alien_review.status_code == 403

    # пробуем изменить свой отзыв
    response_edit_my_review = await ac.put(
        url="/reviews/2",
        json={
            "rating": 5,
            "text": "Очень интересная книга с интересным финалом!"
        }
    )
    response_edit_my_review.status_code == 200
    ac.cookies.clear()