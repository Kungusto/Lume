from tests.schemas.books import TagTitleFromFactory
import factory
from faker import Faker

faker = Faker("ru_RU")


class TagAddFactory(factory.Factory):
    class Meta:
        model = TagTitleFromFactory

    title_tag = factory.LazyAttribute(lambda _: faker.unique.word())
