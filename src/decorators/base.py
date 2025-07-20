from functools import wraps
from src.decorators.utils import make_cache_key, cache_by_key


class BaseCacheManager:
    def __init__(self, redis):
        self.redis = redis._redis

    def base_cache(
        self,
        prefix_key: str = "cache",
        ttl: int = 60,
    ):
        """
        Декоратор для кэширования асинхронных функций с помощью Redis.

        Аналогичен functools.lru_cache, но:
        - Работает с асинхронными функциями
        - Использует Redis в качестве backend
        - Поддерживает TTL (время жизни кэша)

        Ключ кэша формируется из имени функции и аргументов,
        имеющих тип один из: (int, str, float, bool, date)
        """
        def wrapper(func):
            @wraps(func)
            async def inner(*args, **kwargs): 
                key = make_cache_key(prefix_key, func.__name__, args, kwargs)
                return await cache_by_key(redis=self.redis, key=key, ttl=ttl, func=func, *args, **kwargs)
            return inner
        return wrapper

    