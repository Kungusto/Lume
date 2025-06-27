from src.repositories.database.base import BaseRepository
from src.models.reviews import ReviewsORM
from src.schemas.reviews import Review

class ReviewsRepository(BaseRepository):
    model = ReviewsORM
    schema = Review