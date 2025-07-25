from src.exceptions.books import GenreNotFoundException, AuthorNotFoundException

add_book_responses = {
    200: {
        "description": "Успешное изменение публичных данных о пользователе",
        "content": {
            "application/json": {
                "example": {
                    "status": "OK"
                }
            }
        }
    },
    404: {
        "description": "Не найден автор, книга, или жанр",
        "content": {
            "application/json": {
                "examples": {
                    "AuthorNotFound": {
                        "summary": "Указанного автора не существует",
                        "value": {
                            "detail": f"{AuthorNotFoundException.detail}"
                        }
                    },
                    "GenreNotFound": {
                        "summary": "Указанного жанра не существует", 
                        "value": {
                            "detail": f"{GenreNotFoundException.detail}"
                        }
                    }
                }
            }
        }
    }
}