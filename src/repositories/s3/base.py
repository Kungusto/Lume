from fastapi import UploadFile


class BaseS3Repository:
    bucket_name = None

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

    async def get_file_by_path(self, s3_path: str):
        response = await self.client.get_object(Bucket=self.bucket_name, Key=s3_path)
        async with response["Body"] as stream:
            return await stream.read()

    async def delete_by_path(self, s3_path: str):
        await self.client.delete_object(Bucket=self.bucket_name, Key=s3_path)

    async def list_objects_by_prefix(self, prefix: str = ""):
        result = await self.client.list_objects(
            Bucket=self.bucket_name, Prefix="7/images/"
        )
        return result.get("Contents", [])

    async def delete_file(self, path: str):
        await self.client.delete_object(Bucket=self.bucket_name, Key=path)

    async def delete_bulk(self, *args):
        for key in args:
            await self.client.delete_object(Bucket=self.bucket_name, Key=key)
        print("Удаление завершено!")
