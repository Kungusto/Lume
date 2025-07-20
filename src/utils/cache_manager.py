from src.decorators.base import BaseCacheManager
from src.decorators.books import BooksCacheManager
from src.connectors.redis_connector import redis_conn as redis


class CacheManager:
    def __init__(self, redis): 
        self.base = BaseCacheManager(redis=redis).base_cache     
        self.books = BooksCacheManager(redis=redis)


def get_cache_manager():
    return CacheManager(redis=redis)

