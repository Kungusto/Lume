import logging
from celery import Celery
from sqlalchemy import update
from src.config import settings
from src.models.books import BooksORM
from src.api.dependencies import get_sync_session
from src.api.dependencies import get_sync_db_np
import fitz
from src.utils.helpers import PDFRenderer
from src.exceptions.files import FileNotFoundException
from src.schemas.books import Book

celery_app = Celery(
    "tasks",
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL,
    include=["src.tasks.celery_app"],
)


@celery_app.task
def render_book(book_id: int):
    with get_sync_session() as s3:
        try:
            bucket_name = settings.S3_BUCKET_NAME
            response = s3.client.get_object(
                Bucket=bucket_name, Key=f"books/{book_id}/book.pdf"
            )
            with response["Body"] as stream:
                file_pdf = stream.read()
        except s3.client.exceptions.NoSuchKey as ex:
            logging.error(f"не найден файл book.pdf; {settings.S3_BUCKET_NAME=}")
            raise FileNotFoundException from ex

    with fitz.open(stream=file_pdf, filetype="pdf") as doc:
        files_to_add = PDFRenderer.parse_images_from_pdf(doc=doc, book_id=book_id)
        with get_sync_session() as s3:
            for file in files_to_add:
                s3.client.put_object(
                    Key=file["Key"], Bucket=settings.S3_BUCKET_NAME, Body=file["Body"]
                )
    with get_sync_db_np() as db:
        update_stmt = (
            update(BooksORM)
            .filter_by(book_id=book_id)
            .values(is_rendered=True)
            .returning(BooksORM)
        )
        model = db.session.execute(update_stmt)
        result = model.scalar_one()
        book = Book.model_validate(result, from_attributes=True)
        db.commit()
    logging.info(f'Рендеринг книги "{book.title}" завершен')
