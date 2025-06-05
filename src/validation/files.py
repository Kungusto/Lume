from PIL import Image
from io import BytesIO
from src.exceptions.files import (
    WrongFileExpensionException,
    WrongCoverResolutionException,
)
from src.constants.files import AllowedExtensions


class FileValidator:
    @staticmethod
    def check_expansion_images(file_name: str):
        extension = file_name.split(".")[-1]
        if extension not in AllowedExtensions.IMAGES:
            raise WrongFileExpensionException

    @staticmethod
    async def validate_cover(file_img):
        contents = await file_img.read()
        img = Image.open(BytesIO(contents))
        width, height = img.size
        if height <= width:
            raise WrongCoverResolutionException

    @staticmethod
    def check_expansion_books(file_name: str):
        extension = file_name.split(".")[-1]
        if extension not in AllowedExtensions.BOOKS:
            raise WrongFileExpensionException
