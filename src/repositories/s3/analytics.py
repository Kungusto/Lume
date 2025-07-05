from src.repositories.s3.base import BaseS3Repository


class AnalyticsS3Repository(BaseS3Repository):
    prefix_name = "analytics"

    def __init__(self, s3_client):
        self.client = s3_client

    async def save_statement(self, key: str, body):
        await self.client.put_object(Bucket=self.bucket_name, Key=key, Body=body)
