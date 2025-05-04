from src.repositories.s3.base import BaseS3Repository
from fastapi import UploadFile

class BooksS3Repository(BaseS3Repository) :
    bucket_name = "books"

    def __init__(self, s3_client):
        self.client = s3_client

    async def save_cover(self, book_id: int, file: UploadFile) : 
        await self.client.put_object(
            Bucket=self.bucket_name,
            Key=f"{book_id}/preview.png",
            Body=file.file
        )
        return f"{self.bucket_name}/{book_id}/preview.png"
    
    async def save_content(self, book_id: int, file: UploadFile) : 
        await self.client.put_object(
            Bucket=self.bucket_name,
            Key=f"{book_id}/book.pdf",
            Body=file.file
        )
        return f"{self.bucket_name}/{book_id}/book.pdf"


