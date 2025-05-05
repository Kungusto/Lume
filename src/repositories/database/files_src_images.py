from src.models.files_src_images import FilesSrcORM
from src.schemas.books import SourceImage
from src.repositories.database.base import BaseRepository

class FilesRepository(BaseRepository) :
    model = FilesSrcORM
    schema = SourceImage