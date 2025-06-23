import pytest
from src.config import settings


async def test_put_and_get(check_content, s3):
    # Тест на добавление и чтение файла
    new_file_name = "test_image_0.jpg"
    file = await s3.books.get_file_by_path(
        f"other/{new_file_name}", is_content_bucket=True
    )
    await s3.client.put_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{new_file_name}", Body=file
    )
    response = await s3.client.get_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{new_file_name}"
    )
    body = response.get("Body", None)
    assert body

    # Тест метода check_file_by_path
    fake_file_name = "fake_file_name.jpg"
    is_exist = await s3.books.check_file_by_path(f"other/{new_file_name}")
    assert is_exist
    is_exist = await s3.books.check_file_by_path(f"other/{fake_file_name}")
    assert not is_exist

    # Тест на удаление одного файла
    await s3.client.delete_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{new_file_name}"
    )

    try:
        response_after_deletion = await s3.client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=f"other/{new_file_name}"
        )
    except s3.client.exceptions.NoSuchKey:
        response_after_deletion = {}

    body = response_after_deletion.get("Body", None)
    assert not body

    # Тест на удаление нескольких файлов
    new_file_name = "test_image_1.jpg"
    file = await s3.books.get_file_by_path(
        f"other/{new_file_name}", is_content_bucket=True
    )
    await s3.client.put_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{new_file_name}", Body=file
    )
    new_file_name = "test_image_2.jpg"
    file = await s3.books.get_file_by_path(
        f"other/{new_file_name}", is_content_bucket=True
    )
    await s3.client.put_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{new_file_name}", Body=file
    )

    files_with_this_prefix = await s3.books.list_objects_by_prefix("other/")
    await s3.books.delete_bulk(*files_with_this_prefix)
    files_after_deletion = await s3.books.list_objects_by_prefix("other/")
    assert not files_after_deletion


async def test_del_by_prefix(check_content, s3):
    if not check_content:
        pytest.skip()

    target_prefix = "files_to_delete"
    files = await s3.books.get_files_by_prefix(
        f"{target_prefix}/", is_content_bucket=True
    )
    for file in files:
        await s3.client.put_object(
            Bucket=settings.S3_BUCKET_NAME, Key=f"{file['key']}", Body=file["content"]
        )
    files_with_target_prefix = await s3.books.list_objects_by_prefix(
        prefix=target_prefix
    )
    await s3.books.delete_bulk(*files_with_target_prefix)
    files_after_deletion = await s3.books.list_objects_by_prefix(prefix=target_prefix)
    assert not files_after_deletion
