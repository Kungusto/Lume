from src.config import settings

async def add_file(s3):
    print(settings.S3_BUCKET_NAME)

# async def test_list_objects(s3): 
#     files = await s3.books.list_objects_by_prefix("books/")