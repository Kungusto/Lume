import redis.asyncio as redis


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def __aenter__(self):
        self.redis = await redis.Redis(host=self.host, port=self.port)
        return self.redis

    async def __aexit__(self, *args):
        if self.redis:
            await self.redis.close()
