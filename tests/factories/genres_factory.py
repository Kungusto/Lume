import random
from src.schemas.books import GenreAdd
import factory
from faker import Faker

# заранее заготовленный список жанров
from tests.fake_data.genres import BOOK_GENRES

faker = Faker("ru_RU")


class GenreAddFactory(factory.Factory):
    class Meta:
        model = GenreAdd

    title = factory.LazyAttribute(lambda _: generate_genre_title(BOOK_GENRES))


def generate_genre_title(BOOK_GENRES):
    # проверяем, не пуст ли список жанров
    if not BOOK_GENRES:
        return faker.unique.word()
    else:
        return BOOK_GENRES.pop(random.randrange(len(BOOK_GENRES)))
