from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.schemas.users import User

class UsersRepository(BaseRepository) :
    model = UsersOrm
    schema = User
    