from datetime import datetime, timedelta
import factory
from faker import Faker
from tests.schemas.users import BanInfoFromFactory

faker = Faker("ru_RU")


class BanAddFactory(factory.Factory):
    class Meta:
        model = BanInfoFromFactory

    comment = factory.LazyAttribute(lambda _: faker.sentence(nb_words=10))
    ban_until = factory.LazyAttribute(lambda _: datetime.now() + timedelta(days=3))
