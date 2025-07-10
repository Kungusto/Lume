import pytest

"""
Запустить этот файл отдельно: 
pytest -s -v tests/integration/auth/test_api.py
"""


async def test_auth(ac):
    registrate_data = {
        "role": "USER",
        "email": "John123@example.com",
        "name": "John",
        "surname": "Wexler",
        "nickname": "JohnyWex",
        "password": "John_1234",
    }

    response_register = await ac.post(
        url="/auth/register",
        json=registrate_data,
    )

    assert response_register.status_code == 200

    response_login = await ac.post(
        url="/auth/login",
        json={
            "email": registrate_data.get("email"),
            "password": registrate_data.get("password"),
        },
    )

    assert response_login.status_code == 200

    result_logout = await ac.post(url="/auth/logout")
    assert result_logout.status_code == 200


@pytest.mark.parametrize(
    "role, email, name, surname, nickname, password, status_code",
    [
        (
            "USER",
            "user@example.com",
            "John",
            "Smith",
            "johny1",
            "1",
            422,
        ),  # слишком короткий пароль
        (
            "USER",
            "user@example.com",
            "John",
            "Smith",
            "johny1",
            f"{'too_long' * 10}",
            422,
        ),  # слишком длинный пароль
        (
            "USER",
            "John123@example.com",
            "John",
            "Smith",
            "johny1",
            "password",
            409,
        ),  # почта уже зарегистрирована
        (
            "USER",
            "user@example.com",
            "John",
            "Smith",
            "JohnyWex",
            "password",
            409,
        ),  # ник уже занят
        (
            "USER",
            "user@example.com",
            "",
            "Smith",
            "johny1",
            "password",
            422,
        ),  # пустое имя
        (
            "USER",
            "user@example.com",
            "John",
            "",
            "johny1",
            "password",
            422,
        ),  # пустая фамилия
        (
            "USER",
            "user@example.com",
            "John",
            "Smith",
            "johny1",
            "password",
            200,
        ),  # status: OK
    ],
)
async def test_registration(
    ac, role, email, name, surname, nickname, password, status_code
):
    response = await ac.post(
        url="/auth/register",
        json={
            "role": role,
            "email": email,
            "name": name,
            "surname": surname,
            "nickname": nickname,
            "password": password,
        },
    )
    assert response.status_code == status_code


async def test_login(ac, new_user):
    login_data = {"email": new_user.email, "password": new_user.password}

    # логин с неправильной почтой
    response_login = await ac.post(
        url="/auth/login",
        json={"email": "fake@fake.com", "password": new_user.password},
    )
    assert response_login.status_code == 401
    assert not ac.cookies

    # логин с неправильным паролем
    response_login = await ac.post(
        url="/auth/login",
        json={
            "email": new_user.email,
            "password": "qwerty" if new_user.password != "qwerty" else "12345",
        },
    )
    assert response_login.status_code == 401
    assert not ac.cookies

    # логин с правильными данными - 200 OK
    response_login = await ac.post(url="/auth/login", json=login_data)
    assert response_login.status_code == 200
    assert ac.cookies

    # розлогин
    result_logout = await ac.post(url="/auth/logout")
    assert not ac.cookies
    assert result_logout.status_code == 200


async def test_already_authorized(ac, new_user):
    login_data = {"email": new_user.email, "password": new_user.password}
    await ac.post(url="/auth/login", json=login_data)
    response_second = await ac.post(url="/auth/login", json=login_data)
    assert response_second.status_code == 400
    ac.cookies.clear()


async def test_logout(ac, new_user):
    login_data = {"email": new_user.email, "password": new_user.password}
    response_login = await ac.post(
        url="/auth/login",
        json=login_data,
    )
    assert response_login.status_code == 200
    assert ac.cookies

    # выход из аккаунта
    response_logout = await ac.post(url="/auth/logout")
    assert response_logout.status_code == 200
    assert not ac.cookies

    # не авторизован
    response_logout_not_authorized = await ac.post(url="/auth/logout")
    assert response_logout_not_authorized.status_code == 401


async def test_get_me(ac, new_user):
    login_data = {"email": new_user.email, "password": new_user.password}

    response_not_authentificated = await ac.get(url="/auth/me")
    assert response_not_authentificated.status_code == 401

    response_login = await ac.post(
        url="/auth/login",
        json=login_data,
    )

    assert response_login.status_code == 200

    response = await ac.get(url="/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_user.name
    assert data["surname"] == new_user.surname

    ac.cookies.clear()


# async def test_find_user(ac):
#     response = await ac.get(url="auth/1")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Alice"
#     assert data["surname"] == "Johnson"
#     assert data["nickname"] == "ali_jo"

#     response_with_fake_id = await ac.get(url="auth/9999999")
#     assert response_with_fake_id.status_code == 404
