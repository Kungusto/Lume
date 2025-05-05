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
    
    async def delete_all_files_with_prefix(self, prefix: str) :
        try :
            objects_to_delete = []
            paginator = self.client.get_paginator("list_objects_v2")
            async for result in paginator.paginate(Buckket=self.bucket_name, Prefix=prefix) :
                if "Contents" in result :
                    objects_to_delete.extend(
                            [{'Key': obj['Key']} for obj in result['Contents']]
                        )
                for i in range(0, len(objects_to_delete), 1000) :
                    chunk = objects_to_delete[i, i+1000]
                    await self.client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={"Objects": chunk}
                    )                    
        except Exception as e : 
            print(f"Произошла ошибка: {e}")