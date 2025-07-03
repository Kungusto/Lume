from datetime import date
from pydantic import BaseModel, Field


class ReviewAddFromUser(BaseModel):
    rating: int = Field(le=5, ge=1)
    text: str


class ReviewAdd(BaseModel):
    book_id: int
    user_id: int
    text: str
    rating: int = Field(le=5, ge=1)


class Review(ReviewAdd):
    publication_date: date
    review_id: int


class ReviewPut(BaseModel):
    rating: int = Field(le=5, ge=1)
    text: str
