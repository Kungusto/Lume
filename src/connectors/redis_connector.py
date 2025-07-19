import redis.asyncio as redis
from src.config import settings


class RedisManager:
    def __init__(self, host: str, port: int):
        self._redis = redis.Redis(host=host, port=port)

    async def get_client(self):
        return self._redis


redis_conn = RedisManager(settings.REDIS_HOST, settings.REDIS_PORT)
