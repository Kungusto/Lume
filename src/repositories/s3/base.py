from fastapi import UploadFile

class BaseS3Repository :
    bucket_name = None

    def __init__(self, s3_client) : 
        self.client = s3_client

    async def upload_file_by_path(self, localpath: str, s3_path: str) :
        with open(f"src/static/{localpath}", "rb") as file:
            await self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_path,
                Body=file
            )
    
    async def upload_fistapi_file(self, file: UploadFile, s3_path: str) :
        await self.client.put_object(
            Bucket=self.bucket_name,
            Key=s3_path,
            Body=file.file
        )
