from src.exceptions.reviews import (
    RateYourselfHTTPException,
    ReviewAtThisBookAlreadyExistsHTTPException,
    ReviewNotFoundHTTPException,
    CannotEditOthersReviewHTTPException,
    CannotDeleteOthersReviewHTTPException,
)
from src.exceptions.books import BookNotFoundHTTPException

add_review_responses = {
    200: {
        "description": "Отзыв успешно добавлен",
        "content": {
            "application/json": {
                "example": {
                    "review_id": 1,
                    "book_id": 1,
                    "user_id": 1,
                    "rating": 5,
                    "text": "Отличная книга!",
                    "publication_date": "2023-10-01T12:00:00",
                }
            }
        },
    },
    403: {
        "description": "Недостаточно прав для добавления отзыва",
        "content": {
            "application/json": {
                "examples": {
                    "RateYourself": {
                        "summary": "Нельзя оценить свою книгу",
                        "value": {"detail": f"{RateYourselfHTTPException.detail}"},
                    }
                }
            }
        },
    },
    404: {
        "description": "Книга не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotFoundHTTPException.detail}"}
            }
        },
    },
    409: {
        "description": "Отзыв на эту книгу уже существует",
        "content": {
            "application/json": {
                "example": {
                    "detail": f"{ReviewAtThisBookAlreadyExistsHTTPException.detail}"
                }
            }
        },
    },
}

edit_review_responses = {
    200: {
        "description": "Отзыв успешно изменен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для редактирования отзыва",
        "content": {
            "application/json": {
                "example": {"detail": f"{CannotEditOthersReviewHTTPException.detail}"}
            }
        },
    },
    404: {
        "description": "Отзыв не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReviewNotFoundHTTPException.detail}"}
            }
        },
    },
}

delete_review_responses = {
    200: {
        "description": "Отзыв успешно удален",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для удаления отзыва",
        "content": {
            "application/json": {
                "example": {"detail": f"{CannotDeleteOthersReviewHTTPException.detail}"}
            }
        },
    },
    404: {
        "description": "Отзыв не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReviewNotFoundHTTPException.detail}"}
            }
        },
    },
}

get_my_reviews_responses = {
    200: {
        "description": "Список отзывов пользователя успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {
                        "review_id": 1,
                        "book_id": 1,
                        "user_id": 1,
                        "rating": 5,
                        "text": "Отличная книга!",
                        "publication_date": "2023-10-01T12:00:00",
                    }
                ]
            }
        },
    }
}

get_book_reviews_responses = {
    200: {
        "description": "Список отзывов на книгу успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {
                        "review_id": 1,
                        "book_id": 1,
                        "user_id": 1,
                        "rating": 5,
                        "text": "Отличная книга!",
                        "publication_date": "2023-10-01T12:00:00",
                    }
                ]
            }
        },
    }
}
