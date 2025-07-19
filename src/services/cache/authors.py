from pydantic import BaseModel
from src.services.cache.base import BaseCacheService
from src.schemas.books import UserAndBooksWithRels

class AuthorsCacheService(BaseCacheService): 
    async def get_authors_books(self, author_id: int): 
        cached_author = await self._get(f"author:{author_id}:books")
        if not cached_author:
            return None
        
        try: 
            return UserAndBooksWithRels.model_validate(cached_author)
        except Exception:
            return None
        
    async def remember_author_books(self, author_id: int, data: BaseModel) -> None:
        await self._set(key=f"author:{author_id}:books", value=[book.model_dump() for book in data], ttl=300)
