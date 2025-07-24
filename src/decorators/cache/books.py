from functools import wraps
from src.schemas.user_reads import UserBookReadAdd, UserBookReadEdit
from src.decorators.cache.utils import cache_by_key
from src.context.database import get_db_as_context_manager


class BooksCacheManager:
    def __init__(self, redis):
        self.redis = redis._redis

    def page(
        self,
        ttl: int = 60,
    ):
        def wrapper(func):
            @wraps(func)
            async def inner(*args, **kwargs):
                book_id = kwargs.get("book_id")
                page_number = kwargs.get("page_number")
                user_id = kwargs.get("user_id")
                key = f"page:book_id={book_id}:page_number={page_number}"
                page = await cache_by_key(
                    redis=self.redis, key=key, ttl=ttl, func=func, *args, **kwargs
                )
                async with get_db_as_context_manager() as db:
                    user_read_book = await db.user_reads.get_filtered(
                        user_id=user_id, book_id=book_id
                    )
                    if not user_read_book:
                        await db.user_reads.add(
                            UserBookReadAdd(
                                book_id=book_id, user_id=user_id, last_seen_page=page_number
                            )
                        )
                    else:
                        await db.user_reads.edit(
                            UserBookReadEdit(last_seen_page=page_number),
                            user_id=user_id,
                            book_id=book_id,
                        )
                    await db.commit()
                return page
            
            return inner

        return wrapper
