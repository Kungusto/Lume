import pytest
from src.config import settings
from src.utils.s3_manager import S3Client

async def test_s3_file(check_content):
    if not check_content:
        pytest.skip()

    new_file_name = "test_image_0.jpg"
    async with S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_URL,
        region_name=settings.S3_REGION
    ) as s3:
        file = await s3.books.get_file_by_path(f"other/{new_file_name}", test=True)
        await s3.client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=new_file_name,
            Body=file
        )

# async def test_list_objects(s3): 
#     files = await s3.books.list_objects_by_prefix("books/")