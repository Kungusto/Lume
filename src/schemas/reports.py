from datetime import datetime
from pydantic import BaseModel


class ReportAdd(BaseModel):
    reason_id: int
    book_id: int


class BanAdd(BaseModel):
    user_id: int
    ban_until: datetime
    comment: str


class ReasonAdd(BaseModel):
    title: str


class Report(ReportAdd):
    id: int


class Ban(BaseModel):
    ban_id: int


class Reason(BaseModel):
    reason_id: int