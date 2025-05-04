from fastapi import APIRouter, UploadFile, BackgroundTasks
from src.api.dependencies import S3Dep, DBDep, UserIdDep
from src.schemas.books import BookAdd, BookAddWithAuthors
from src.schemas.books import BookPATCHOnPublication
from src.tasks.taskiq_tasks import async_render

router = APIRouter(prefix="/books", tags=["Книги"])

@router.post("/book")
async def add_book(data: BookAddWithAuthors, db: DBDep) : 
    book = await db.books.add(BookAdd(**data.model_dump()))
    await db.commit()
    return {"status": "OK", "data": book}

@router.post("/cover")
async def add_cover(file: UploadFile, book_id: int, user_id: UserIdDep, db: DBDep, s3: S3Dep) :
    await db.books.get_one(book_id=book_id)
    cover_link = await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=cover_link)
          )
    return {"status": "OK"}

@router.post("/content")
async def add_all_content(file: UploadFile, book_id: int, s3: S3Dep) : 
    await s3.books.save_content(book_id, file=file)
    await async_render.kiq(book_id=book_id)
    return {"status": "OK"}
