from aiobotocore.session import get_session as async_get_session
from aiobotocore.config import AioConfig
from botocore.session import get_session as sync_get_session
from botocore.config import Config
from src.repositories.s3.books import BooksS3Repository
from src.repositories.s3.analytics import AnalyticsS3Repository


class AsyncS3Client:
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
            "config": AioConfig(s3={"addressing_style": "virtual"}),
        }
        self.session = async_get_session()

    async def __aenter__(self):
        self.client = await self.session.create_client("s3", **self.config).__aenter__()

        self.books = BooksS3Repository(self.client)
        self.analytics = AnalyticsS3Repository(self.client)

        return self

    async def __aexit__(self, *args):
        await self.client.close()


class SyncS3Client:
    """Класс, предназначенный исключительно для Celery. Не использовать в бизнес логике!"""

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
            "config": Config(s3={"addressing_style": "virtual"}),
        }
        self.session = sync_get_session()

    def __enter__(self):
        self.client = self.session.create_client("s3", **self.config)

        return self

    def __exit__(self, *args):
        self.client.close()
