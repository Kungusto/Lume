from src.services.auth import AuthService

def test_access_token_service() :
    data = {"user_id": 1}
    jwt_token = AuthService().create_access_token(data=data)
    decoded = AuthService().decode_token(jwt_token)
    assert jwt_token
    assert isinstance(jwt_token, str)
    assert decoded.get("user_id", None) == 1
    assert decoded["user_id"] == data["user_id"]

def test_hash_password() :
    password = "TEST_1234"
    hashed_password = AuthService().hash_password(password=password)
    assert isinstance(hashed_password, str)
    assert AuthService().verify_password(
        plain_password=password,
        hashed_password=hashed_password
    )
