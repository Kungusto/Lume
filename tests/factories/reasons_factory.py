from src.schemas.reports import ReasonAdd
import factory
from faker import Faker

faker = Faker("ru_RU")


class TagAddFactory(factory.Factory):
    class Meta:
        model = ReasonAdd

    title = factory.LazyAttribute(lambda _: faker.unique.word())
