import factory
from faker import Faker
from src.schemas.users import UserAdd

fake = Faker("ru_RU")


class UserAddFactory(factory.Factory):
    class Meta:
        model = UserAdd

    role = "USER"
    email = factory.Sequence(lambda n: f"{fake.user_name()}_{n}@user.com")
    name = factory.LazyAttribute(lambda _: fake.first_name())
    surname = factory.LazyAttribute(lambda _: fake.last_name())
    nickname = factory.Sequence(lambda n: f"{fake.user_name()}_{n}")
    hashed_password = factory.LazyAttribute(lambda _: fake.password(length=10))


class AuthorsAddFactory(UserAddFactory):
    role = "AUTHOR"


class AdminAddFactory(UserAddFactory):
    role = "ADMIN"


class GeneralAdminAddFactory(UserAddFactory):
    role = "GENERAL_ADMIN"
