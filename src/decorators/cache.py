from datetime import timedelta
from functools import wraps
import pickle
from src.connectors.redis_connector import redis_conn as redis
import logging
import time

def make_cache_key(prefix: str, func_name: str, args, kwargs):
    clean_args = []
    for arg in args:
        if isinstance(arg, (int, str, float, bool)) or arg is None:
            clean_args.append(str(arg))
    for k, v in kwargs.items():
        if isinstance(v, (int, str, float, bool)) or v is None:
            clean_args.append(f"{k}={v}")
    return f"{prefix}:{func_name}:{':'.join(clean_args)}"


def redis_cache(
    prefix_key: str = "cache",
    ttl: int = 60,
):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs): 
            key = make_cache_key(prefix_key, func.__name__, args, kwargs)
            
            cached = await redis._redis.get(key)
            if cached:
                logging.debug(f"Функция: {func.__name__} была закеширована")
                return pickle.loads(cached)
            
            res = await func(*args, **kwargs)
            await redis._redis.setex(
                name=key,
                time=timedelta(seconds=ttl),
                value=pickle.dumps(res)
            )
            return res
        return inner
    return wrapper


