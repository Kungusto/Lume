from src.exceptions.auth import (
    NickAlreadyRegistratedHTTPException,
    EmailAlreadyRegistratedHTTPException,
    NotAuthentificatedHTTPException,
)


register_responses = {
    200: {
        "description": "Успешная регистрация",
        "content": {
            "application/json": {
                "example": {
                    "user_id": 33,
                    "role": "USER",
                    "email": "kate@example.com",
                    "name": "Катя",
                    "surname": "Смирнова",
                    "nickname": "katerina88",
                    "last_activity": "2025-07-25T08:58:22.977947Z",
                    "registation_date": "2025-07-25T08:58:22.977947Z",
                }
            }
        },
    },
    409: {
        "description": "Занят ник, либо почта",
        "content": {
            "application/json": {
                "examples": {
                    "EmailAlreadyExists": {
                        "summary": "Почта уже занята",
                        "value": {
                            "detail": f"{EmailAlreadyRegistratedHTTPException.detail}",
                        },
                    },
                    "NickAlreadyExists": {
                        "summary": "Ник уже занят",
                        "value": {
                            "detail": f"{NickAlreadyRegistratedHTTPException.detail}",
                        },
                    },
                }
            }
        },
    },
    422: {"description": "Пароль короче 5 символов, или длинней 50"},
}

login_responses = {
    200: {
        "description": "Успешный логин",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozMiwicm9sZSI6IlVTRVIiLCJleHAiOjE3NTM0MzY0ODl9.bk9RKnhWftd0BrfF35qNOE5vongaVlctie2CKxPum3k"
                }
            }
        },
    },
    400: {
        "description": "Пользователь уже аутентифицирован",
        "content": {
            "application/json": {"example": {"detail": "Вы уже аутентифицированы"}}
        },
    },
    401: {
        "description": "Неправильный пароль, или почта",
        "content": {
            "application/json": {
                "example": {"detail": "Неправильный пароль, либо почта"}
            }
        },
    },
}


info_current_user_responses = {
    200: {
        "description": "Успешное получение данных о текущем пользователе",
        "content": {
            "application/json": {
                "example": {
                    "user_id": 1,
                    "role": "USER",
                    "email": "ivan@example.com",
                    "name": "Иван",
                    "surname": "Иванов",
                    "nickname": "ivan_the_best",
                    "last_activity": "2025-07-25T10:07:37.162419Z",
                    "registation_date": "2025-07-25T10:07:16.404139Z",
                }
            }
        },
    },
    401: {
        "description": "Пользователь не аутентифицирован",
        "content": {
            "application/json": {
                "example": {"detail": f"{NotAuthentificatedHTTPException.detail}"}
            }
        },
    },
}


logout_responses = {
    200: {
        "description": "Успешный выход из аккаунта",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    401: {
        "description": "Пользователь не аутентифицирован",
        "content": {
            "application/json": {"example": {"detail": "Вы не аутентифицированы"}}
        },
    },
}


info_about_user_responses = {
    200: {
        "description": "Успешный поиск данных о пользователе",
        "content": {
            "application/json": {
                "example": {
                    "name": "Иван",
                    "surname": "Иванов",
                    "nickname": "ivan_the_best",
                }
            }
        },
    },
    404: {
        "descipription": "Пользователя с этим id не существует",
        "content": {
            "application/json": {"example": {"detail": "Пользователь не найден"}}
        },
    },
}


edit_user_data_responses = {
    200: {
        "description": "Успешное изменение публичных данных о пользователе",
        "content": {"application/json": {"example": {"status": "OK"}}},
    },
    404: {
        "descipription": "Пользователя с этим id не существует",
        "content": {
            "application/json": {"example": {"detail": "Пользователь не найден"}}
        },
    },
}
