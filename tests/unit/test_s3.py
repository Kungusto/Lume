from src.config import settings
from tests.utils import FileManager


async def test_put_and_get(check_content_for_tests, s3):
    # Тест на добавление и чтение файла
    all_files_in_other = await FileManager().get_files_in_folder("other")
    file, filename = all_files_in_other[0]

    await s3.client.put_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{filename}", Body=file
    )
    response = await s3.client.get_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{filename}"
    )
    body = response.get("Body", None)
    assert body

    # Тест метода check_file_by_path
    fake_file_name = f"unreal_prefix/unreal_file.txt"
    is_exist = await s3.books.check_file_by_path(f"other/{filename}")
    assert is_exist
    is_exist = await s3.books.check_file_by_path(fake_file_name)
    assert not is_exist

    # Тест на удаление одного файла
    await s3.client.delete_object(
        Bucket=settings.S3_BUCKET_NAME, Key=f"other/{filename}"
    )

    try:
        response_after_deletion = await s3.client.get_object(
            Bucket=settings.S3_BUCKET_NAME, Key=f"other/{filename}"
        )
    except s3.client.exceptions.NoSuchKey:
        response_after_deletion = {}

    body = response_after_deletion.get("Body", None)
    assert not body


async def test_del_by_prefix(check_content_for_tests, s3):
    all_files_in_other = await FileManager().get_files_in_folder("other")
    target_prefix = "files_to_delele"

    for file, filename in all_files_in_other:
        await s3.client.put_object(
            Bucket=settings.S3_BUCKET_NAME, Key=f"{target_prefix}/{filename}", Body=file
        )
    files_with_target_prefix = await s3.books.list_objects_by_prefix(
        prefix=target_prefix
    )
    await s3.books.delete_bulk(*files_with_target_prefix)
    files_after_deletion = await s3.books.list_objects_by_prefix(prefix=target_prefix)
    assert not files_after_deletion
