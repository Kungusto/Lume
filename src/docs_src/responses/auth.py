from src.exceptions.auth import NickAlreadyRegistratedHTTPException, EmailAlreadyRegistratedHTTPException


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
                        "registation_date": "2025-07-25T08:58:22.977947Z"
                    }   
                }
            }
        },
        409: {
            "description": "Занят ник, либо почта",
            "content": {
                "application/json": {
                    "examples": {
                        "EmailAlreadyExists": {
                            "summary": "Почта уже занята",
                            "value":
                            {
                                "detail": f"{EmailAlreadyRegistratedHTTPException.detail}",
                            }
                        },
                        "NickAlreadyExists": {
                            "summary": "Ник уже занят",
                            "value":
                            {
                                "detail": f"{NickAlreadyRegistratedHTTPException.detail}",
                            }
                        }                        
                    }
                }
            }
        },
        422: {
            "description": "Пароль короче 5 символов, или длинней 50"
        }
}

login_responses = {
    200: {
        "description": "Успешный логин",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozMiwicm9sZSI6IlVTRVIiLCJleHAiOjE3NTM0MzY0ODl9.bk9RKnhWftd0BrfF35qNOE5vongaVlctie2CKxPum3k"                }        
            }
        }
    },
    400: {
        "description": "Пользователь уже аутентифицирован",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Вы уже аутентифицированы"
                }
            }
        }
    },
    401: {
        "description": "Неправильный пароль, или почта",
        "content": {
            "application/json": {
                "example": {
                 "detail": "Неправильный пароль, либо почта"
                }
            }
        }
    }
}