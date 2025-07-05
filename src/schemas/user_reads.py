from datetime import datetime, timezone
from pydantic import BaseModel


class UserBookRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    started_at: datetime = datetime.now(timezone.utc)
    last_seen_page: int


class UserBookReadAdd(BaseModel):
    user_id: int
    book_id: int
    last_seen_page: int


class UserBookReadEdit(BaseModel):
    last_seen_page: int
