from src.services.cache.authors import AuthorsCacheService
from src.services.cache.users import UsersCacheService

class CacheManager:
    def __init__(self, redis): 
        self.users = UsersCacheService(redis=redis)
        self.authors = AuthorsCacheService(redis=redis)
        
    