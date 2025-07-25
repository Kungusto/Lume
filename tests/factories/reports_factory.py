import factory
from faker import Faker
from tests.schemas.users import ReportCommentFromFactory

faker = Faker("ru_RU")


class ReportAddFactory(factory.Factory):
    class Meta:
        model = ReportCommentFromFactory

    comment = factory.LazyAttribute(lambda _: faker.sentence(nb_words=8))
