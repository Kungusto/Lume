from tests.fake_data.genres import BOOK_GENRES
from src.schemas.books import GenreAdd
import factory
from faker import Faker
faker = Faker("ru_RU")


class GenreAddFactory(factory.Factory):
    class Meta:
        model = GenreAdd

    title = factory.LazyAttribute(lambda _: faker.unique.word(ext_word_list=BOOK_GENRES))
