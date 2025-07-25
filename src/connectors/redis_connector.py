import redis.asyncio as async_redis
import redis as sync_redis
from src.config import settings


class RedisManager:
    def __init__(self, host: str, port: int):
        self._redis = async_redis.Redis(host=host, port=port)

    async def get_client(self):
        return self._redis


redis_conn = RedisManager(settings.REDIS_HOST, settings.REDIS_PORT)
redis_sync_conn = sync_redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
