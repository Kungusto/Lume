import logging
from pydantic import BaseModel
from src.services.cache.base import BaseCacheService
from src.schemas.users import User


class UsersCacheService(BaseCacheService):
    async def get_cached_user(self, user_id: int):
        cached_user = await self._get(f"user:{user_id}")
        if not cached_user:
            return None

        try:
            return User.model_validate(cached_user)
        except Exception:
            logging.warning(
                f"У пользователя {user_id} в кеше хранятся битые данные, либо их нет"
            )
            return None

    async def remember_user(self, user_id: int, data: BaseModel) -> None:
        await self._set(key=f"user:{user_id}", value=data.model_dump(), ttl=300)
