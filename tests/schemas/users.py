from datetime import datetime
from pydantic import BaseModel
from src.schemas.users import User


class TestUserWithPassword(User):
    password: str


class ReportCommentFromFactory(BaseModel):
    comment: str


class BanInfoFromFactory(BaseModel):
    comment: str
    ban_until: datetime


class TestBanInfo(BaseModel):
    ban_id: int
    user_id: int
    comment: str
    ban_until: datetime
