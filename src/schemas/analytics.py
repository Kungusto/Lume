from datetime import timedelta
from pydantic import BaseModel

"""Здесь будут схемы с данными для аналитики"""


# активности пользователей, количестве отзывов и оценок, популярности книг и авторах


# started_at | ended_at | active_users_in_week |  active_users_in_statement_interval | new_reviews | new_users


class UsersStatementWithoutDate(BaseModel):
    active_users_in_week: int
    active_users_in_statement_interval: int
    new_reviews: int
    new_users: int


class UsersStatement(BaseModel):
    started_date_as_str: str
    ended_date_as_str: str
    active_users_in_week: int
    active_users_in_statement_interval: int
    new_reviews: int
    new_users: int


# Указание интервала админом
class StatementRequestFromADMIN(BaseModel):
    interval: timedelta
