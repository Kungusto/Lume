"""
Временный файл! Создан для проверки работоспособности фабрик

Запустить этот файл отдельно:
pytest -s -v tests/unit/test_factory.py
"""


async def test_login(db, ac, new_user):
    auth_ac = await ac.post(
        url="/auth/login", json={"email": new_user.email, "password": new_user.password}
    )
    assert auth_ac.status_code == 200
    assert ac.cookies
