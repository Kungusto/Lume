from src.services.auth import AuthService

def test_access_token_service() :
    data = {"user_id": 1}
    jwt_token = AuthService().create_access_token(data=data)
    decoded = AuthService().decode_token(jwt_token)
    assert jwt_token
    assert isinstance(jwt_token, str)
    assert decoded.get("user_id", None)
    assert decoded.get("user_id", None) == 1
