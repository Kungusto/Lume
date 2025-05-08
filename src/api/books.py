from fastapi import APIRouter, UploadFile, BackgroundTasks
from src.exceptions.exceptions import CoverNotFoundHTTPException
from src.api.dependencies import S3Dep, DBDep, UserIdDep
from src.models.files_src_images import FilesSrcORM
from src.schemas.books import (
    BookAdd,
    BookAddWithAuthorsTagsGenres, 
    BookPATCHWithRels, 
    BookPATCHOnPublication, 
    TagAdd, 
    GenresBooksAdd, 
    BookPATCH,
    TagEdit
)
from src.tasks.taskiq_tasks import async_render, async_delete_book
from src.schemas.books_authors import BookAuthorAdd

router = APIRouter(prefix="/author", tags=["Авторы и публикация книг"])

@router.post("")
async def add_book(data: BookAddWithAuthorsTagsGenres, db: DBDep, user_id: UserIdDep) : 
    data.authors.append(user_id)
    book = await db.books.add(BookAdd(**data.model_dump()))
    data_to_add_m2m = [BookAuthorAdd(book_id=book.book_id, author_id=author) for author in data.authors]
    data_to_tags_m2m = [TagAdd(book_id=book.book_id, title_tag=title) for title in data.tags]
    data_to_genres_m2m = [GenresBooksAdd(book_id=book.book_id, genre_id=gen_id) for gen_id in data.genres]
    await db.books_authors.add_bulk(data_to_add_m2m)
    await db.tags.add_bulk(data_to_tags_m2m)
    await db.books_genres.add_bulk(data_to_genres_m2m)
    await db.commit()
    return {"status": "OK", "data": book}

@router.post("/cover")
async def add_cover(file: UploadFile, book_id: int, db: DBDep, s3: S3Dep) :
    cover_link = await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=cover_link)
          )
    await db.commit()
    return {"status": "OK"}

@router.put("/cover")
async def add_cover(file: UploadFile, book_id: int, db: DBDep, s3: S3Dep) :
    book = await db.books.get_one(book_id=book_id)
    if not book.cover_link :
        raise CoverNotFoundHTTPException
    await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=f"{book_id}/preview.png")
          )
    await db.commit()
    return {"status": "OK"}

@router.post("/content")
async def add_all_content(file: UploadFile, book_id: int, s3: S3Dep) : 
    await s3.books.save_content(book_id, file=file)
    await async_render.kiq(book_id=book_id)
    return {"status": "OK"}

@router.get("/book")
async def get_book_by_id(book_id: int, db: DBDep) : 
    return await db.books.get_book_with_rels(book_id=book_id)

@router.get("/my_books")
async def get_my_books(user_id: UserIdDep, db: DBDep) :
    return await db.users.get_books_by_user(user_id=user_id)

@router.patch("/book")
async def edit_bood_data(book_id: int, db: DBDep, data: BookPATCHWithRels) : 
    book_patch_data = BookPATCH(**data.model_dump(exclude_unset=True))
    genres = await db.books_genres.get_filtered(book_id=book_id)
    genres_ids_in_db = [genre.id for genre in genres] 
    new_tags = data.genres 
    same_els = (set(genres_ids_in_db) & set(new_tags))
    genres_to_add =  set(new_tags) - same_els
    genres_to_delete = set(genres_ids_in_db) - same_els
    data_to_add_genres = [GenresBooksAdd(genre_id=gen_book_id, book_id=book_id) for gen_book_id in genres_to_add]
    if genres_to_delete :
        await db.books_genres.delete_bulk_by_ids(genres_to_delete, book_id=book_id) 
    if genres_to_add :
        await db.books_genres.add_bulk(data_to_add_genres) 
    if book_patch_data.model_dump(exclude_unset=True) :
        await db.books.edit(data=book_patch_data, is_patch=True, book_id=book_id)
    await db.commit()
    return {"status": "OK"}

@router.delete("/book")
async def delete_book(book_id: int, db: DBDep, s3: S3Dep) :
    book = await db.books.get_one(book_id=book_id)
    await db.books_authors.delete(book_id=book_id)
    await async_delete_book.kiq(book_id=book_id)
    if book.is_rendered :
        await s3.books.delete_by_path(f"{book_id}/book.pdf")
    if book.cover_link :
        await s3.books.delete_by_path(f"{book_id}/preview.png")
    await db.files.delete(book_id=book_id)
    await db.books.delete(book_id=book_id)
    await db.commit()
    return {"status": "OK"}

@router.put("/content")
async def edit_content(book_id: int, content: UploadFile, s3: S3Dep, db: DBDep) :
    await async_delete_book.kiq(book_id=book_id)    
    await s3.books.save_content(book_id=book_id, file=content)
    await async_render.kiq(book_id=book_id)
    await db.commit()
    return {"status": "OK"}
