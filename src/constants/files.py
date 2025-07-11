class AllowedExtensions:
    IMAGES = {"jpg", "jpeg", "png", "webp"}
    BOOKS = {"pdf"}


class RequiredFilesForTests:
    INTEGRATION_TESTS_FILES = {
        "content": {
            # контент книг
            "test_book.pdf",
            "test_book_2.pdf",
            "not_a_book.jpg",
        },
        "covers": {
            # обложки книг
            "not_a_cover.pdf",
            "not_tall_enough.jpg",
            "normal_cover.jpg",
        },
    }
