class Permissions:
    ROLES_PREFIXES = {
        "USER":          {"auth", "books", "reviews"},
        "AUTHOR":        {"auth", "books", "reviews", "author"},
        "ADMIN":         {"admin", "auth", "books", "reviews", "author"},
        "GENERAL_ADMIN": {"admin", "auth", "books", "reviews", "author"},
    }

    # Публичные маршруты с регулярными выражениями
    # Ручки, доступные незарегистрированым пользователям
    PUBLIC_ENDPOINTS = {
        (r"^/auth/\d+$", "GET"),
        (r"^/books$", "GET"),
        (r"^/books/genres$", "GET"),
        (r"^/books/\d+$", "GET"),
        (r"^/books/download/\d+$", "GET"),
        (r"^/reviews/by_book/\d+$", "GET"),
        ("/auth/login", "POST"),
        ("/auth/logout", "POST"),
        ("/auth/register", "POST"),
    }

