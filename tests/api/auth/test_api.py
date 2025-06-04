from aiohttp import ClientSession

async def test_api_registration():
    async with ClientSession() as session : 
        response = await session.post(
            url="http://127.0.0.1:8000/auth/register",
            json={
                "role": "USER",
                "email": "duck_in_the_truck@gmail.com",
                "name": "Lidia",
                "surname": "Adams",
                "nickname": "LidiaDuck12",
                "password": "Duck_panda_L98"
            }
        )
        assert response.status == 200
        # логин
        # данные о себе
        # данные о другом пользователе
        # разлогин
        ...


        