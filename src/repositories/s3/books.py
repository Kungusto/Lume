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
            response = await self.client.delete_object(
                Bucket=self.bucket_name,
                Key="7/images/page_1_img_1.png"
            )                        
            print(response)
            # async for page in paginator.paginate(
            #     Bucket=self.bucket_name,
            #     Prefix=prefix
            # ) :
            #     if "Contents" in page: 
            #         for obj in page["Contents"] :
            #             files.append(obj["Key"])
                        
            # print(files)
            # print(paginator)
            # async for result in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix) :
            #     if "Contents" in result :
            #         objects_to_delete.extend(
            #                 [{'Key': obj['Key']} for obj in result['Contents']]
            #             )
            #     for i in range(0, len(objects_to_delete), 1000) :
            #         chunk = objects_to_delete[i, i+1000]
            #         deleted = await self.client.delete_objects(
            #             Bucket=self.bucket_name,
            #             Delete={"Objects": chunk}
            #         )         
            #         print(deleted)           
        except Exception as e : 
            print(f"Произошла ошибка: {e}")
