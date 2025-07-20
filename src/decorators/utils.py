from datetime import date, timedelta
import pickle
from typing import Callable


def make_cache_key(prefix: str, func_name: str, args, kwargs):
    clean_args = []
    for arg in args:
        if isinstance(arg, (int, str, float, bool, date)) or arg is None:
            clean_args.append(str(arg))
    for k, v in kwargs.items():
        if isinstance(v, (int, str, float, bool, date)) or v is None:
            clean_args.append(f"{k}={v}")
    return f"{prefix}:{func_name}:{':'.join(clean_args)}"


async def cache_by_key(redis, key: str, ttl: int, func: Callable, *args, **kwargs):
    """
    Содержит в себе основную логику кеша.

    Вызывается везде одинаково:
    return await cache_by_key(redis=self.redis, key=key, ttl=ttl, func=func, *args, **kwargs)
    """
    cached = await redis.get(key)
    if cached:
        return pickle.loads(cached)

    res = await func(*args, **kwargs)
    await redis.setex(name=key, time=timedelta(seconds=ttl), value=pickle.dumps(res))
    return res
