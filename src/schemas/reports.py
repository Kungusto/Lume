from datetime import date, datetime, timedelta, timezone
from pydantic import BaseModel, field_validator
from src.exceptions.reports import InvalidBanDateHTTPException


class ReportAdd(BaseModel):
    reason_id: int
    book_id: int
    comment: str | None = None


class ReportAddFromUser(BaseModel):
    reason_id: int
    comment: str | None = None


class BanAdd(BaseModel):
    user_id: int
    ban_until: datetime = datetime.now(timezone.utc) + timedelta(hours=1)
    comment: str


class BanAddFromUser(BaseModel):
    ban_until: datetime = datetime.now(timezone.utc) + timedelta(hours=1)
    comment: str

    @field_validator("ban_until")
    @classmethod
    def check_date(cls, value: date) -> date:
        if value.tzinfo is None:
            # Если пришёл naive datetime — делаем его UTC
            value = value.replace(tzinfo=timezone.utc)
        if value > datetime.now(timezone.utc):
            return value
        else:
            raise InvalidBanDateHTTPException


class ReasonAdd(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def tags_to_lower(cls, value: str) -> list[str]:
        return value.lower()


class Report(ReportAdd):
    id: int
    is_checked: bool = False


class Ban(BanAdd):
    ban_id: int


class ReasonEdit(ReasonAdd): ...


class BanEdit(BaseModel):
    ban_until: datetime = datetime.now(timezone.utc) + timedelta(hours=1)


class Reason(ReasonAdd):
    reason_id: int
