import random
from tests.schemas.books import TagTitleFromFactory
import factory
from faker import Faker

# заранее заготовленный список жанров
from tests.fake_data.genres import BOOK_GENRES 

faker = Faker("ru_RU")


class TagAddFactory(factory.Factory):
    class Meta:
        model = TagTitleFromFactory

    title_tag = factory.LazyAttribute(lambda _: faker.unique.word())
