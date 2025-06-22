import pytest
from src.config import settings
from src.utils.s3_manager import S3Client

async def test_s3_file(check_content, s3):
    if not check_content:
        pytest.skip()

    new_file_name = "test_image_0.jpg"
    file = await s3.books.get_file_by_path(f"other/{new_file_name}", is_content_bucket=True)
    await s3.client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=f"other/{new_file_name}",
        Body=file
    )
    response = await s3.client.get_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=f"other/{new_file_name}"
    )
    assert response.get("Body", None)