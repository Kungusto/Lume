from aiobotocore.session import get_session
from aiobotocore.config import AioConfig
from src.repositories.s3.books import BooksS3Repository


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        region_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
            "config": AioConfig(s3={"addressing_style": "virtual"})
        }
        self.session = get_session()

    async def __aenter__(self):
        self.client = await self.session.create_client("s3", **self.config).__aenter__()

        self.books = BooksS3Repository(self.client)

        return self

    async def __aexit__(self, *args):
        await self.client.close()
