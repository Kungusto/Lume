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
    def users_data_sql(now: datetime, interval: timedelta):
        interval = text("interval '5 minutes'")
        query = select(
            select(func.count("*"))
            .select_from(UsersORM)
            .filter(UsersORM.last_activity + interval > now)
            .label("active_users"),
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
