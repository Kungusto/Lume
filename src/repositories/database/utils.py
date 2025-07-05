from datetime import datetime, timedelta
from sqlalchemy import select, text, func
from src.models.users import UsersORM
from src.models.reviews import ReviewsORM

"""
-- started_at | ended_at | active_users | new_reviews | new_users

select
(
select now() as started_at
),
(
select now() + interval '7days' as ended_at
),
(
select count(*) as active_users from "Users" u
where u.last_activity + interval '7 days' > now()
),
(
select count(*) as new_reviews from "Reviews" r
where r.publication_date + interval '7 days' > now()
),
(
select count(*) as new_users from "Users" u
where u.registation_date + interval '7 days' > now()
);
"""


class AnalyticsQueryFactory:
    """Генерирует SQL для получения различных отчетов"""

    @staticmethod
    def users_data_sql(now: datetime, interval_td: timedelta = timedelta(minutes=5)):
        interval = text(timedelta_to_sql_interval(interval_td))
        query = select(
            select(func.count("*"))
            .select_from(UsersORM)
            .filter(UsersORM.last_activity + text("interval '7 days'") > now)
            .label("active_users_in_week"),
            select(func.count("*"))
            .select_from(UsersORM)
            .filter(UsersORM.last_activity + interval > now)
            .label("active_users_in_statement_interval"),
            select(func.count("*"))
            .select_from(ReviewsORM)
            .filter(ReviewsORM.publication_date + interval > now)
            .label("new_reviews"),
            select(func.count("*"))
            .select_from(UsersORM)
            .filter(UsersORM.registation_date + interval > now)
            .label("new_users"),
        )
        return query


def timedelta_to_sql_interval(td: timedelta) -> str:
    days = td.days
    seconds = td.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} days")
    if hours:
        parts.append(f"{hours} hours")
    if minutes:
        parts.append(f"{minutes} minutes")
    if seconds:
        parts.append(f"{seconds} seconds")

    interval_str = " ".join(parts)
    return f"interval '{interval_str}'"
