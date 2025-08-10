from src.exceptions.books import (
    AuthorNotFoundException,
    BookNotFoundException,
    GenreNotFoundException,
    CoverNotFoundException,
    ContentNotFoundException,
    BookNotExistsOrYouNotOwnerException,
    CoverAlreadyExistsException,
    ContentAlreadyExistsException,
    BookAlreadyPublicatedException,
)
from src.exceptions.files import (
    WrongFileExpensionException,
    WrongCoverResolutionException,
)

add_book_responses = {
    200: {
        "description": "Успешное изменение публичных данных о пользователе",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Не найден автор, книга, или жанр",
        "content": {
            "application/json": {
                "examples": {
                    "AuthorNotFound": {
                        "summary": "Указанного автора не существует",
                        "value": {"detail": f"{AuthorNotFoundException.detail}"},
                    },
                    "GenreNotFound": {
                        "summary": "Указанного жанра не существует",
                        "value": {"detail": f"{GenreNotFoundException.detail}"},
                    },
                }
            }
        },
    },
}


edit_book_responses = {
    200: {
        "description": "Данные о книге успешно изменены",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для изменения книги",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    404: {
        "description": "Не найдена книга или жанр",
        "content": {
            "application/json": {
                "examples": {
                    "BookNotFound": {
                        "summary": "Книга не найдена",
                        "value": {"detail": f"{BookNotFoundException.detail}"},
                    },
                    "GenreNotFound": {
                        "summary": "Жанр не найден",
                        "value": {"detail": f"{GenreNotFoundException.detail}"},
                    },
                }
            }
        },
    },
}

delete_book_responses = {
    200: {
        "description": "Книга успешно удалена",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для удаления книги",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    404: {
        "description": "Книга не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotFoundException.detail}"}
            }
        },
    },
}

get_my_books_responses = {
    200: {
        "description": "Список книг автора",
        "content": {
            "application/json": {
                "example": [
                    {
                        "user_id": 18,
                        "role": "GENERAL_ADMIN",
                        "email": "ADMIN@admin.com",
                        "name": "string",
                        "surname": "string",
                        "nickname": "ADMIN",
                        "last_activity": "2025-07-25T16:48:16.293529Z",
                        "registation_date": "2025-06-26T21:00:00Z",
                        "books": [
                            {
                                "book_id": 53,
                                "title": "string",
                                "age_limit": 0,
                                "description": "string",
                                "language": "English",
                                "date_publicated": "2025-07-24",
                                "is_rendered": True,
                                "render_status": "uploaded",
                                "cover_link": None,
                                "is_publicated": False,
                                "total_pages": 13,
                                "authors": [
                                    {
                                        "name": "string",
                                        "surname": "string",
                                        "nickname": "ADMIN",
                                    }
                                ],
                                "tags": [],
                                "genres": [{"genre_id": 1, "title": "Фэнтези"}],
                                "reviews": [],
                            },
                        ],
                    }
                ]
            }
        },
    }
}

add_cover_responses = {
    200: {
        "description": "Обложка успешно добавлена",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для добавления обложки",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    409: {
        "description": "Обложка уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{CoverAlreadyExistsException.detail}"}
            }
        },
    },
    422: {
        "description": "Ошибка валидации файла",
        "content": {
            "application/json": {
                "examples": {
                    "WrongFileExpension": {
                        "summary": "Неправильное расширение файла",
                        "value": {"detail": f"{WrongFileExpensionException.detail}"},
                    },
                    "WrongCoverResolution": {
                        "summary": "Неправильное разрешение обложки",
                        "value": {"detail": f"{WrongCoverResolutionException.detail}"},
                    },
                }
            }
        },
    },
}

put_cover_responses = {
    200: {
        "description": "Обложка успешно обновлена",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для обновления обложки",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    404: {
        "description": "Обложка не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{CoverNotFoundException.detail}"}
            }
        },
    },
    422: {
        "description": "Ошибка валидации файла",
        "content": {
            "application/json": {
                "examples": {
                    "WrongFileExpension": {
                        "summary": "Неправильное расширение файла",
                        "value": {"detail": f"{WrongFileExpensionException.detail}"},
                    },
                    "WrongCoverResolution": {
                        "summary": "Неправильное разрешение обложки",
                        "value": {"detail": f"{WrongCoverResolutionException.detail}"},
                    },
                }
            }
        },
    },
}

add_all_content_responses = {
    200: {
        "description": "Контент книги успешно добавлен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для добавления контента",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    404: {
        "description": "Книга не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotFoundException.detail}"}
            }
        },
    },
    409: {
        "description": "Контент уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{ContentAlreadyExistsException.detail}"}
            }
        },
    },
    422: {
        "description": "Неправильное расширение файла",
        "content": {
            "application/json": {
                "example": {"detail": f"{WrongFileExpensionException.detail}"}
            }
        },
    },
}

edit_content_responses = {
    200: {
        "description": "Контент книги успешно обновлен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для обновления контента",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    404: {
        "description": "Контент не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{ContentNotFoundException.detail}"}
            }
        },
    },
    422: {
        "description": "Неправильное расширение файла",
        "content": {
            "application/json": {
                "example": {"detail": f"{WrongFileExpensionException.detail}"}
            }
        },
    },
}

publicate_book_responses = {
    200: {
        "description": "Книга успешно опубликована",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для публикации книги",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotExistsOrYouNotOwnerException.detail}"}
            }
        },
    },
    404: {
        "description": "Не найдена книга, контент или обложка",
        "content": {
            "application/json": {
                "examples": {
                    "BookNotFound": {
                        "summary": "Книга не найдена",
                        "value": {"detail": f"{BookNotFoundException.detail}"},
                    },
                    "ContentNotFound": {
                        "summary": "Контент не найден",
                        "value": {"detail": f"{ContentNotFoundException.detail}"},
                    },
                    "CoverNotFound": {
                        "summary": "Обложка не найдена",
                        "value": {"detail": f"{CoverNotFoundException.detail}"},
                    },
                }
            }
        },
    },
    409: {
        "description": "Книга уже опубликована",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookAlreadyPublicatedException.detail}"}
            }
        },
    },
}


get_publication_status_responses = {
    200: {
        "description": "Статус публикации успешно получен",
        "content": {
            "application/json": {
                "example": {"render_status": "rendered"}
            }
        }
    },
    404: {
        "description": "Книга не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{BookNotFoundException.detail}"}
            }
        },
    },
}