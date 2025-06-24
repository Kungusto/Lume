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
        "books/test_book.pdf",
        "books/test_cover.jpg",
    }
