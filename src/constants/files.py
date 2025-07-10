class AllowedExtensions:
    IMAGES = {"jpg", "jpeg", "png", "webp"}
    BOOKS = {"pdf"}


class RequiredFilesForTests:
    # обычные изображения для unit-тестов
    UNIT_TESTS_FILES = {
        "other/test_image_0.jpg",
        "other/test_image_1.jpg",
        "other/test_image_2.jpg",
    }
    INTEGRATION_TESTS_FILES = {
        # контент книг
        "books/content/test_book.pdf",
        "books/content/test_book_2.jpg",
        "books/content/not_a_book.jpg",
        # обложки книг
        "books/covers/not_a_cover.pdf",
        "books/covers/not_tall_enough.jpg",
        "books/covers/normal_cover.jpg",
    }
