import redis.asyncio as redis
import redis as sync_redis



class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.session = None

    async def __aenter__(self):
        self.session = await redis.Redis(host=self.host, port=self.port)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()


    def __enter__(self):
        self.session = sync_redis.Redis(host=self.host, port=self.port)
        return self


    def __exit__(self, *args):
        if self.session:
            self.session.close()