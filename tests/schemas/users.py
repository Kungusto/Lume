from src.schemas.users import User


class TestUserWithPassword(User):
    password: str
