from functools import wraps
from src.decorators.cache.utils import cache_by_key


class BooksCacheManager:
    def __init__(self, redis):
        self.redis = redis._redis

    def page(
        self,
        ttl: int = 60,
    ):
        def wrapper(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                book_id = kwargs.get("book_id")
                page_number = kwargs.get("page_number")
                key = f"page:book_id={book_id}:page_number={page_number}"
                return await cache_by_key(
                    redis=self.redis, key=key, ttl=ttl, func=func, *args, **kwargs
                )

            return inner

        return wrapper
