from fastapi import UploadFile
from src.config import settings

class BaseS3Repository:
    bucket_name: str = settings.S3_BUCKET_NAME

    def __init__(self, s3_client):
        self.client = s3_client

    async def upload_file_by_path(self, localpath: str, s3_path: str):
        with open(f"src/static/{localpath}", "rb") as file:
            await self.client.put_object(
                Bucket=self.bucket_name, Key=s3_path, Body=file
            )

    async def upload_fistapi_file(self, file: UploadFile, s3_path: str):
        await self.client.put_object(
            Bucket=self.bucket_name, Key=s3_path, Body=file.file
        )

    async def check_file_by_path(self, s3_path: str):
        try:
            await self.client.head_object(Bucket=self.bucket_name, Key=s3_path)
            return True
        except self.client.exceptions.NoSuchKey:
            return False
        except Exception:
            return False

    async def get_file_by_path(self, s3_path: str, is_content_bucket = False):
        if is_content_bucket:
            bucket_name = settings.S3_STATIC_BUCKET_NAME
        else:
            bucket_name = settings.S3_BUCKET_NAME
        response = await self.client.get_object(Bucket=bucket_name, Key=s3_path)
        async with response["Body"] as stream:
            return await stream.read()

    async def delete_by_path(self, s3_path: str):
        await self.client.delete_object(Bucket=self.bucket_name, Key=s3_path)

    async def delete_file(self, path: str):
        await self.client.delete_object(Bucket=self.bucket_name, Key=path)

    async def delete_bulk(self, *args):
        for key in args:
            await self.client.delete_object(Bucket=self.bucket_name, Key=key)

    async def list_objects_by_prefix(self, prefix: str = "", is_content_bucket = False) -> list[str]:
        """Вернуть список всех ключей (имён файлов), соответствующих префиксу."""
        if is_content_bucket:
            bucket_name = settings.S3_STATIC_BUCKET_NAME
        else:
            bucket_name = settings.S3_BUCKET_NAME
        response = await self.client.list_objects_v2(
            Prefix=prefix,
            Bucket=bucket_name
        )
        contents = response.get("Contents", [])
        result = [file["Key"] for file in contents]
        return result

