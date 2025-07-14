from pydantic import BaseModel
from src.schemas.users import User


class TestUserWithPassword(User):
    password: str


class ReportCommentFromFactory(BaseModel):
    comment: str
