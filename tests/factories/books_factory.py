import random
import factory
from faker import Faker
from src.schemas.books import BookAdd
from src.enums.books import LanguagesEnum


faker = Faker("ru_RU")


class BookAddFactory(factory.Factory):
    class Meta:
        model = BookAdd

    title = factory.LazyAttribute(lambda _: faker.sentence(nb_words=3).rstrip("."))
    age_limit = factory.LazyAttribute(lambda _: random.randrange(1, 21))
    description = factory.LazyAttribute(lambda _: faker.sentence(nb_words=10))
    language = factory.LazyAttribute(lambda _: random.choice(list(LanguagesEnum)))
