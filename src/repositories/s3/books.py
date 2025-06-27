from src.repositories.s3.base import BaseS3Repository
from fastapi import UploadFile


class BooksS3Repository(BaseS3Repository):
    prefix_name = "books"

    def __init__(self, s3_client):
        self.client = s3_client

    async def save_cover(self, book_id: int, file: UploadFile):
        await file.seek(0)
        await self.client.put_object(
            Bucket=self.bucket_name,
            Key=f"{self.prefix_name}/{book_id}/preview.png",
            Body=file.file,
        )
        return f"{self.prefix_name}/{book_id}/preview.png"

    async def save_content(self, book_id: int, file: UploadFile):
        await file.seek(0)
        await self.client.put_object(
            Bucket=self.bucket_name,
            Key=f"{self.prefix_name}/{book_id}/book.pdf",
            Body=file.file,
        )
        print(f"{self.prefix_name}/{book_id}/book.pdf")
        return f"{self.prefix_name}/{book_id}/book.pdf"
