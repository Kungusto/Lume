from src.exceptions.books import (
    BookNotFoundHTTPException,
    CannotDeleteGenreHTTPException,
    GenreAlreadyExistsHTTPException,
    GenreNotFoundHTTPException,
    TagAlreadyExistsHTTPException,
    TagNotFoundHTTPException,
)
from src.exceptions.auth import (
    UserNotFoundHTTPException,
    ChangePermissionsOfADMINHTTPException,
)
from src.exceptions.reports import (
    AlreadyBannedHTTPException,
    ReasonAlreadyExistsHTTPException,
    ReasonNotFoundHTTPException,
    ReportNotFoundHTTPException,
    UserNotBannedHTTPException,
)
from src.exceptions.files import (
    StatementNotFoundHTTPException,
)

change_role_responses = {
    200: {
        "description": "Роль пользователя успешно изменена",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Недостаточно прав для изменения роли",
        "content": {
            "application/json": {
                "example": {"detail": f"{ChangePermissionsOfADMINHTTPException.detail}"}
            }
        },
    },
    404: {
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{UserNotFoundHTTPException.detail}"}
            }
        },
    },
}

add_genre_responses = {
    200: {
        "description": "Жанр успешно добавлен",
        "content": {
            "application/json": {"example": {"genre_id": 1, "title": "Фэнтези"}}
        },
    },
    409: {
        "description": "Жанр с таким названием уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{GenreAlreadyExistsHTTPException.detail}"}
            }
        },
    },
}

edit_genre_responses = {
    200: {
        "description": "Жанр успешно изменен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Жанр не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{GenreNotFoundHTTPException.detail}"}
            }
        },
    },
    409: {
        "description": "Жанр с таким названием уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{GenreAlreadyExistsHTTPException.detail}"}
            }
        },
    },
}

delete_genre_responses = {
    200: {
        "description": "Жанр успешно удален",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    403: {
        "description": "Нельзя удалить жанр, на который ссылаются книги",
        "content": {
            "application/json": {
                "example": {"detail": f"{CannotDeleteGenreHTTPException.detail}"}
            }
        },
    },
    404: {
        "description": "Жанр не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{GenreNotFoundHTTPException.detail}"}
            }
        },
    },
}

add_tag_responses = {
    200: {
        "description": "Тег успешно добавлен",
        "content": {
            "application/json": {
                "example": {"id": 1, "book_id": 1, "title_tag": "приключения"}
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
        "description": "Тег уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{TagAlreadyExistsHTTPException.detail}"}
            }
        },
    },
}

delete_tag_responses = {
    200: {
        "description": "Тег успешно удален",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Тег не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{TagNotFoundHTTPException.detail}"}
            }
        },
    },
}

edit_tag_responses = {
    200: {
        "description": "Тег успешно изменен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Тег не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{TagNotFoundHTTPException.detail}"}
            }
        },
    },
    409: {
        "description": "Тег с таким названием уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{TagAlreadyExistsHTTPException.detail}"}
            }
        },
    },
}

add_reason_responses = {
    200: {
        "description": "Причина жалобы успешно добавлена",
        "content": {
            "application/json": {"example": {"id": 1, "title": "Неприемлемый контент"}}
        },
    },
    409: {
        "description": "Причина жалобы уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReasonAlreadyExistsHTTPException.detail}"}
            }
        },
    },
}

edit_reason_responses = {
    200: {
        "description": "Причина жалобы успешно изменена",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Причина жалобы не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReasonNotFoundHTTPException.detail}"}
            }
        },
    },
    409: {
        "description": "Причина жалобы с таким названием уже существует",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReasonAlreadyExistsHTTPException.detail}"}
            }
        },
    },
}

delete_reason_responses = {
    200: {
        "description": "Причина жалобы успешно удалена",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Причина жалобы не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReasonNotFoundHTTPException.detail}"}
            }
        },
    },
}

get_not_checked_reports_responses = {
    200: {
        "description": "Список непроверенных жалоб успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {
                        "reason_id": 2,
                        "book_id": 1,
                        "comment": "string",
                        "id": 1,
                        "is_checked": False,
                    }
                ]
            }
        },
    }
}

mark_as_checked_responses = {
    200: {
        "description": "Жалоба отмечена как проверенная",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Жалоба не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{ReportNotFoundHTTPException.detail}"}
            }
        },
    },
}

ban_user_by_id_responses = {
    200: {
        "description": "Пользователь успешно заблокирован",
        "content": {
            "application/json": {
                "user_id": 1,
                "ban_until": "2030-01-01T00:00:00Z",
                "comment": "Вы забанены до 2030 года :o",
                "ban_id": 2,
            }
        },
    },
    403: {
        "description": "Недостаточно прав для блокировки пользователя",
        "content": {
            "application/json": {
                "example": {"detail": f"{ChangePermissionsOfADMINHTTPException.detail}"}
            }
        },
    },
    404: {
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{UserNotFoundHTTPException.detail}"}
            }
        },
    },
    409: {
        "description": "Пользователь уже забанен",
        "content": {
            "application/json": {
                "example": {"detail": f"{AlreadyBannedHTTPException.detail}"}
            }
        },
    },
}

unban_user_by_ban_id_responses = {
    200: {
        "description": "Пользователь успешно разбанен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Блокировка не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{UserNotBannedHTTPException.detail}"}
            }
        },
    },
}

edit_ban_date_responses = {
    200: {
        "description": "Срок бана успешно изменен",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "description": "Блокировка не найдена",
        "content": {
            "application/json": {
                "example": {"detail": f"{UserNotBannedHTTPException.detail}"}
            }
        },
    },
}

get_banned_users_responses = {
    200: {
        "description": "Список заблокированных пользователей успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {
                        "user_id": 1,
                        "role": "USER",
                        "email": "user@example.com",
                        "name": "Иван",
                        "surname": "Иванов",
                        "nickname": "ivanov",
                        "last_activity": "2025-07-25T10:30:00",
                        "registation_date": "2025-01-01T00:00:00",
                        "ban_until": "2025-12-31T23:59:59",
                    }
                ]
            }
        },
    }
}

generate_report_inside_app_responses = {
    200: {
        "description": "Отчет успешно сгенерирован",
        "content": {
            "application/json": {
                "example": {
                    "path": "s3://reports/users_2025-07-25_10-30-00.xlsx",
                    "url": "https://s3.example.com/reports/users_2025-07-25_10-30-00.xlsx",
                }
            }
        },
    }
}

get_statements_by_date_responses = {
    200: {
        "description": "Список отчетов за указанную дату успешно получен",
        "content": {
            "application/json": {
                "example": [
                    {
                        "path": "s3://reports/users_2025-07-25_10-30-00.xlsx",
                        "url": "https://s3.example.com/reports/users_2025-07-25_10-30-00.xlsx",
                    }
                ]
            }
        },
    }
}

save_and_get_auto_statement_responses = {
    200: {
        "description": "Автоматический отчет успешно сохранен и получен",
        "content": {
            "application/json": {
                "example": {
                    "url": "https://s3.example.com/reports/users_statement_auto.xlsx"
                }
            }
        },
    },
    404: {
        "description": "Автоматический отчет не найден",
        "content": {
            "application/json": {
                "example": {"detail": f"{StatementNotFoundHTTPException.detail}"}
            }
        },
    },
}
# [
#   {
#     "key": "analytics/2025-07-06/users_2025-07-06_09-32-09.xlsx",
#     "url": "https://lume-s3.s3.ru-7.storage.selcloud.ru/analytics/2025-07-06/users_2025-07-06_09-32-09.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=a0e7c68227b84515b54c6002f7d5bed2%2F20250725%2Fru-7%2Fs3%2Faws4_request&X-Amz-Date=20250725T193803Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=929f37119dd77fa642ddb54a3abf1baf482f849d521b24fe0e3104e920b4033c"
#   },
#   {
#     "key": "analytics/2025-07-06/users_2025-07-06_09-33-03.xlsx",
#     "url": "https://lume-s3.s3.ru-7.storage.selcloud.ru/analytics/2025-07-06/users_2025-07-06_09-33-03.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=a0e7c68227b84515b54c6002f7d5bed2%2F20250725%2Fru-7%2Fs3%2Faws4_request&X-Amz-Date=20250725T193803Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=3ec0186272818b00b44925291c741d3bcc4bc505e587290bd67b13e3c80ddd0d"
#   },
#   {
#     "key": "analytics/2025-07-06/users_2025-07-06_09-33-26.xlsx",
#     "url": "https://lume-s3.s3.ru-7.storage.selcloud.ru/analytics/2025-07-06/users_2025-07-06_09-33-26.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=a0e7c68227b84515b54c6002f7d5bed2%2F20250725%2Fru-7%2Fs3%2Faws4_request&X-Amz-Date=20250725T193803Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d2deaadd113a5814006b5a234cf3277c4d50e4a4f58358e513e6e2c5a05ea4e6"
#   },
#   {
#     "key": "analytics/2025-07-06/users_2025-07-06_09-34-17.xlsx",
#     "url": "https://lume-s3.s3.ru-7.storage.selcloud.ru/analytics/2025-07-06/users_2025-07-06_09-34-17.xlsx?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=a0e7c68227b84515b54c6002f7d5bed2%2F20250725%2Fru-7%2Fs3%2Faws4_request&X-Amz-Date=20250725T193803Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=bc66d4a5e8430ba398fb9dc6af961db9a2c6281a1688d1a1f926759ce2f87fab"
#   }
# ]
