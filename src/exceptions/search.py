from src.exceptions.base import BadRequestHTTPException, BadRequestException


class MinAgeGreaterThanMaxAgeHTTPException(BadRequestHTTPException):
    detail = "min_age не может быть больше max_age"


class LaterThanAfterEarlierThanHTTPException(BadRequestHTTPException):
    detail = "later_than не может быть позже earlier_than"


class MinRatingGreaterThanMaxRatingHTTPException(BadRequestHTTPException):
    detail = "min_rating не может быть больше max_rating"


class MinReadersGreaterThanMaxReadersHTTPException(BadRequestHTTPException):
    detail = "min_readers не может быть больше max_readers"


class MinAgeGreaterThanMaxAgeException(BadRequestException):
    detail = "min_age не может быть больше max_age"


class LaterThanAfterEarlierThanException(BadRequestException):
    detail = "later_than не может быть позже earlier_than"


class MinRatingGreaterThanMaxRatingException(BadRequestException):
    detail = "min_rating не может быть больше max_rating"


class MinReadersGreaterThanMaxReadersException(BadRequestException):
    detail = "min_readers не может быть больше max_readers"
