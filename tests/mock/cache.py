from typing import Callable


async def fake_cache_by_key(redis, key: str, ttl: int, func: Callable, *args, **kwargs):
    """Мокируем функцию cache_by_key()"""
    return await func(*args, **kwargs)
