import asyncio
import logging
from src.api.dependencies import get_async_session
from src.api.dependencies import get_db_np
import fitz
from taskiq_redis import RedisStreamBroker
from src.config import get_settings, settings
from src.utils.helpers import PDFRenderer
from src.exceptions.files import FileNotFoundException

settings = get_settings()
broker = RedisStreamBroker(settings.REDIS_URL)


@broker.task
async def async_render(book_id: int):
    files = []
    async for s3 in get_async_session():
        try:
            file_pdf = await s3.books.get_file_by_path(f"books/{book_id}/book.pdf")
        except s3.client.exceptions.NoSuchKey as ex:
            logging.error(f"не найден файл book.pdf; {settings.S3_BUCKET_NAME=}")
            raise FileNotFoundException from ex


    with fitz.open(stream=file_pdf, filetype="pdf") as doc:
        files_to_add = PDFRenderer.parse_images_from_pdf(doc, book_id=book_id)
        async for s3 in get_async_session():
            for file in files_to_add:
                await s3.books.client.put_object(
                    Key=file["Key"], Bucket="books", Body=file["Body"]
                )
    async for db in get_db_np():
        book = await db.books.mark_as_rendered(book_id=book_id)
        await db.commit()
    logging.info(f'Рендеринг книги "{book.title}" завершен')


@broker.task
async def async_delete_book(book_id: int):
    async for db in get_db_np():
        books = await db.files.get_filtered(book_id=book_id)
        await db.files.delete(book_id=book_id)
        await db.commit()
    files = [book.src for book in books]
    async for s3 in get_async_session():
        await s3.books.delete_bulk(*files)


@broker.task
async def ping_task():
    return "pong"
