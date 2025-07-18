from datetime import timedelta
import orjson
from typing import Any, Dict


class BaseCacheService:
    def __init__(self, redis):
        self.redis = redis

    async def _get(self, key: str) -> Dict[str, Any] | None:
        cached_data = await self.redis.get(key)
        return orjson.loads(cached_data) if cached_data else None

    async def _set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> None:
        await self.redis.setex(
            key,
            timedelta(seconds=ttl),
            orjson.dumps(
                value, option=orjson.OPT_NAIVE_UTC | orjson.OPT_OMIT_MICROSECONDS
            ),
        )

    async def _invalidate(self, key: str):
        await self.redis.delete(key)
