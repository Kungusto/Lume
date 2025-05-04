from fastapi import APIRouter, UploadFile, BackgroundTasks
from src.exceptions.exceptions import CoverNotFoundHTTPException
from src.api.dependencies import S3Dep, DBDep, UserIdDep
from src.schemas.books import BookAdd, BookAddWithAuthors, BookPATCH
from src.schemas.books import BookPATCHOnPublication
from src.tasks.taskiq_tasks import async_render
from src.schemas.books_authors import BookAuthorAdd

router = APIRouter(prefix="/author", tags=["Авторы и публикация книг"])

@router.post("")
async def add_book(data: BookAddWithAuthors, db: DBDep, user_id: UserIdDep) : 
    data.authors.append(user_id)
    book = await db.books.add(BookAdd(**data.model_dump()))
    data_to_add_m2m = [BookAuthorAdd(book_id=book.book_id, author_id=author) for author in data.authors]
    await db.books_authors.add_bulk(data_to_add_m2m)
    await db.commit()
    return {"status": "OK", "data": book}

@router.post("/cover")
async def add_cover(file: UploadFile, book_id: int, db: DBDep, s3: S3Dep) :
    cover_link = await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=cover_link)
          )
    return {"status": "OK"}

@router.put("/cover")
async def add_cover(file: UploadFile, book_id: int, db: DBDep, s3: S3Dep) :
    book = await db.books.get_one(book_id=book_id)
    if not book.cover_link :
        raise CoverNotFoundHTTPException
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

@router.get("")
async def get_book_by_id(book_id: int, db: DBDep) : 
    return await db.books.get_book_with_rels(book_id=book_id)

@router.patch("")
async def edit_bood_data(book_id: int, db: DBDep, data: BookPATCH) : 
    await db.books.edit(data=data, is_patch=True, book_id=book_id)
    await db.commit()
    return {"status": "OK"}

@router.delete("")
async def delete_book(book_id: int, db: DBDep, s3: S3Dep) :
    await db.books.delete(book_id=book_id)
    await s3.books.list_objects_by_prefix()
    return {"status": "OK"}