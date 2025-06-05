import pytest


async def test_auth(ac):
    response_register = await ac.post(
        url="/auth/register",
        json={
            "role": "USER",
            "email": "John123@example.com",
            "name": "John",
            "surname": "Wexler",
            "nickname": "JohnyWex",
            "password": "John_1234",
        },
    )

    assert response_register.status_code == 200

    response_login = await ac.post(
        url="/auth/login",
        json={"email": "John123@example.com", "password": "John_1234"},
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


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("user1@example.com", "johny", 401),
        ("user@example.com", "johny1", 401),
        ("user@example.com", "password", 200),
    ],
)
async def test_login(ac, email, password, status_code):
    auth_ac = await ac.post(
        url="/auth/login", json={"email": email, "password": password}
    )
    assert auth_ac.status_code == status_code
    if status_code != 200:
        return
    assert ac.cookies

    result_logout = await ac.post(url="/auth/logout")

    assert not ac.cookies
    assert result_logout.status_code == 200


async def test_already_authorized(ac):
    await ac.post(
        url="/auth/login", json={"email": "user@example.com", "password": "password"}
    )
    response_second = await ac.post(
        url="/auth/login", json={"email": "user@example.com", "password": "password"}
    )
    assert response_second.status_code == 400

    ac.cookies.clear()


async def test_logout(ac):
    response_login = await ac.post(
        url="/auth/login",
        json={"email": "John123@example.com", "password": "John_1234"},
    )

    assert response_login.status_code == 200
    assert ac.cookies

    response_logout = await ac.post(url="/auth/logout")

    assert response_logout.status_code == 200
    assert not ac.cookies

    response_logout_not_authorized = await ac.post(url="/auth/logout")

    assert response_logout_not_authorized.status_code == 401


async def test_get_me(ac):
    response_not_authentificated = await ac.get(url="/auth/me")
    assert response_not_authentificated.status_code == 401

    response_login = await ac.post(
        url="/auth/login",
        json={"email": "John123@example.com", "password": "John_1234"},
    )

    assert response_login.status_code == 200

    response = await ac.get(url="/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John"
    assert data["surname"] == "Wexler"

    ac.cookies.clear()


async def test_find_user(ac):
    response = await ac.get(url="auth/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["surname"] == "Johnson"
    assert data["nickname"] == "ali_jo"

    response_with_fake_id = await ac.get(url="auth/9999999")
    assert response_with_fake_id.status_code == 404
