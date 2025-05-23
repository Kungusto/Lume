import logging
from src.api.dependencies import get_session
from src.api.dependencies import get_db_np
import fitz
from taskiq_redis import RedisStreamBroker
from src.config import settings
from src.schemas.books import SourceImageAdd

broker = RedisStreamBroker(settings.REDIS_URL)


@broker.task
async def async_render(book_id: int):
    files = []
    async for s3 in get_session():
        file_pdf = await s3.books.get_file_by_path(f"{book_id}/book.pdf")
    with fitz.open(stream=file_pdf, filetype="pdf") as doc:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            images_list = page.get_images(full=True)
            for img_index, img in enumerate(images_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_key = (
                    f"{book_id}/images/page_{page_num + 1}_img_{img_index + 1}.png"
                )
                file_to_add = SourceImageAdd(src=image_key, book_id=book_id)
                files.append(file_to_add)
                async for s3 in get_session():
                    await s3.books.client.put_object(
                        Key=image_key, Bucket="books", Body=image_bytes
                    )
    async for db in get_db_np():
        book = await db.books.mark_as_rendered(book_id=book_id)
        if files:
            await db.files.add_bulk(files)
        await db.commit()
    logging.info(f'Рендеринг книги "{book.title}" завершен')


@broker.task
async def async_delete_book(book_id: int):
    async for db in get_db_np():
        books = await db.files.get_filtered(book_id=book_id)
        await db.files.delete(book_id=book_id)
        await db.commit()
    files = [book.src for book in books]
    async for s3 in get_session():
        await s3.books.delete_bulk(*files)
