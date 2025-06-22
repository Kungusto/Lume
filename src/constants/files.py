class AllowedExtensions:
    IMAGES = {"jpg", "jpeg", "png", "webp"}
    BOOKS = {"pdf"}


class RequiredFilesForTests:
    # обычные изображения для unit-тестов
    FILES = {
        "other/test_image_0.jpg",
        "other/test_image_1.jpg",
        "other/test_image_2.jpg",
    }
