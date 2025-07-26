from src.exceptions.books import (
    BookNotFoundHTTPException,
    ContentNotFoundHTTPException,
)
from src.exceptions.search import (
    LaterThanAfterEarlierThanHTTPException,
    MinAgeGreaterThanMaxAgeHTTPException,
    MinRatingGreaterThanMaxRatingHTTPException,
    MinReadersGreaterThanMaxReadersHTTPException,
)
from src.exceptions.reports import ReasonNotFoundHTTPException

get_filtered_publicated_books_with_pagination_responses = {
    200: {
        "description": "Список книг успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {
                        "book_id": 1,
                        "title": "Python. К Вершинам мастерства",
                        "age_limit": 16,
                        "description": "string",
                        "language": "English",
                        "date_publicated": "2025-07-24",
                        "is_rendered": True,
                        "render_status": "uploaded",
                        "cover_link": None,
                        "is_publicated": True,
                        "total_pages": 898,
                        "authors": [
                            {"name": "string", "surname": "string", "nickname": "ADMIN"}
                        ],
                        "tags": [
                            {"id": 3, "book_id": 1, "title_tag": "python"},
                            {"id": 4, "book_id": 1, "title_tag": "string"},
                        ],
                        "genres": [{"genre_id": 1, "title": "Фэнтези"}],
                        "reviews": [],
                        "avg_rating": None,
                        "readers": 1,
                    },
                    {
                        "book_id": 2,
                        "title": "Unit тестирование",
                        "age_limit": 16,
                        "description": "string",
                        "language": "English",
                        "date_publicated": "2025-07-24",
                        "is_rendered": True,
                        "render_status": "ready",
                        "cover_link": None,
                        "is_publicated": True,
                        "total_pages": 10,
                        "authors": [
                            {"name": "string", "surname": "string", "nickname": "ADMIN"}
                        ],
                        "tags": [{"id": 1, "book_id": 2, "title_tag": "pytest"}],
                        "genres": [{"genre_id": 1, "title": "Фэнтези"}],
                        "reviews": [],
                        "avg_rating": None,
                        "readers": 1,
                    },
                ]
            }
        },
    },
    400: {
        "description": "Некорректные параметры фильтрации",
        "content": {
            "application/json": {
                "examples": {
                    "LaterThanAfterEarlierThan": {
                        "summary": "Неправильный диапазон дат",
                        "value": {
                            "detail": f"{LaterThanAfterEarlierThanHTTPException.detail}"
                        },
                    },
                    "MinAgeGreaterThanMaxAge": {
                        "summary": "Неправильный диапазон возрастов",
                        "value": {
                            "detail": f"{MinAgeGreaterThanMaxAgeHTTPException.detail}"
                        },
                    },
                    "MinRatingGreaterThanMaxRating": {
                        "summary": "Неправильный диапазон рейтингов",
                        "value": {
                            "detail": f"{MinRatingGreaterThanMaxRatingHTTPException.detail}"
                        },
                    },
                    "MinReadersGreaterThanMaxReaders": {
                        "summary": "Неправильный диапазон читателей",
                        "value": {
                            "detail": f"{MinReadersGreaterThanMaxReadersHTTPException.detail}"
                        },
                    },
                }
            }
        },
    },
}

get_all_genres_responses = {
    200: {
        "description": "Список жанров успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {"genre_id": 1, "title": "Фэнтези"},
                    {"genre_id": 2, "title": "Научная фантастика"},
                ]
            }
        },
    }
}

get_book_by_id_responses = {
    200: {
        "description": "Книга успешно получена",
        "content": {
            "application/json": {
                "example": {
                    "book_id": 1,
                    "title": "Python. К Вершинам мастерства",
                    "age_limit": 16,
                    "description": "string",
                    "language": "English",
                    "date_publicated": "2025-07-24",
                    "is_rendered": True,
                    "render_status": "uploaded",
                    "cover_link": None,
                    "is_publicated": True,
                    "total_pages": 898,
                    "authors": [
                        {"name": "string", "surname": "string", "nickname": "ADMIN"}
                    ],
                    "tags": [
                        {"id": 4, "book_id": 1, "title_tag": "string"},
                        {"id": 3, "book_id": 1, "title_tag": "python"},
                    ],
                    "genres": [{"genre_id": 1, "title": "Фэнтези"}],
                    "reviews": [],
                    "avg_rating": None,
                    "readers": 1,
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
}

download_book_responses = {
    200: {
        "description": "URL для скачивания книги успешно получен",
        "content": {
            "application/json": {
                "example": {"url": "https://example.com/books/1/book.pdf"}
            }
        },
    },
    404: {
        "description": "Книга или контент не найдены",
        "content": {
            "application/json": {
                "examples": {
                    "BookNotFound": {
                        "summary": "Книга не найдена",
                        "value": {"detail": f"{BookNotFoundHTTPException.detail}"},
                    },
                    "ContentNotFound": {
                        "summary": "Контент книги не найден",
                        "value": {"detail": f"{ContentNotFoundHTTPException.detail}"},
                    },
                }
            }
        },
    },
}

get_page_responses = {
    200: {
        "description": "Страница книги успешно получена",
        "content": {
            "application/json": {
                "example": [
                    {"type": "text", "content": "Текст страницы"},
                    {"type": "image", "path": "https://example.com/images/page1.jpg"},
                ]
            }
        },
    },
    404: {
        "description": "Книга, контент или страница не найдены",
        "content": {
            "application/json": {
                "examples": {
                    "BookNotFound": {
                        "summary": "Книга не найдена",
                        "value": {"detail": f"{BookNotFoundHTTPException.detail}"},
                    },
                    "ContentNotFound": {
                        "summary": "Контент книги не найден",
                        "value": {"detail": f"{ContentNotFoundHTTPException.detail}"},
                    },
                    "PageNotFound": {
                        "summary": "Страница не найдена",
                        "value": {"detail": "Страница 5 не найдена"},
                    },
                }
            }
        },
    },
}

report_book_responses = {
    200: {
        "description": "Жалоба на книгу успешно подана",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "book_id": 1,
                    "reason_id": 1,
                    "description": "Неприемлемый контент",
                }
            }
        },
    },
    404: {
        "description": "Книга или причина жалобы не найдены",
        "content": {
            "application/json": {
                "examples": {
                    "BookNotFound": {
                        "summary": "Книга не найдена",
                        "value": {"detail": f"{BookNotFoundHTTPException.detail}"},
                    },
                    "ReasonNotFound": {
                        "summary": "Причина жалобы не найдена",
                        "value": {"detail": f"{ReasonNotFoundHTTPException.detail}"},
                    },
                }
            }
        },
    },
}
