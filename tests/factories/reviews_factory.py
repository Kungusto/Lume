from src.schemas.reviews import ReviewAddFromUser
import factory
import random
from faker import Faker

faker = Faker("ru_RU")


class ReviewAddFactory(factory.Factory):
    class Meta:
        model = ReviewAddFromUser

    rating = factory.LazyAttribute(lambda _: random.randint(1, 5))
    text = factory.LazyAttribute(lambda _: faker.sentence(nb_words=10))
