from pydantic import BaseModel, Field


class ReviewAddFromUser(BaseModel):
    rating: int = Field(le=5, ge=1)


class ReviewAdd(BaseModel):
    book_id: int
    user_id: int
    rating: int = Field(le=5, ge=1)


class Review(ReviewAdd):
    review_id: int


class ReviewPut(BaseModel):
    rating: int
