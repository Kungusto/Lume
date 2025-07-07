from datetime import date
from src.exceptions.search import (
    LaterThanAfterEarlierThanException,
    MinAgeGreaterThanMaxAgeException,
    MinRatingGreaterThanMaxRatingException,
    MinReadersGreaterThanMaxReadersException,
)


class SearchValidator:
    @staticmethod
    def validate_book_filters(
        max_age: int | None,
        min_age: int | None,
        later_than: date | None,
        earlier_than: date | None,
        min_rating: float | None,
        max_rating: float | None,
        min_readers: int | None,
        max_readers: int | None,
        *args,
        **kwargs,
    ):
        # Валидация пар
        if min_age is not None and max_age is not None and min_age > max_age:
            raise MinAgeGreaterThanMaxAgeException
        if (
            later_than is not None
            and earlier_than is not None
            and later_than > earlier_than
        ):
            raise LaterThanAfterEarlierThanException
        if (
            min_rating is not None
            and max_rating is not None
            and min_rating > max_rating
        ):
            raise MinRatingGreaterThanMaxRatingException
        if (
            min_readers is not None
            and max_readers is not None
            and min_readers > max_readers
        ):
            raise MinReadersGreaterThanMaxReadersException
