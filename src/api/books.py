from fastapi import APIRouter, UploadFile
from src.services.auth import AuthService
from src.exceptions.exceptions import (
    CoverNotFoundHTTPException,
    ContentAlreadyExistsHTTPException,
    BookNotFoundHTTPException,
    BookNotFoundException,
)
from src.api.dependencies import S3Dep, DBDep, UserRoleDep, authorize_and_return_user_id
from src.schemas.books import (
    BookAdd,
    BookAddWithAuthorsTagsGenres,
    BookPATCHWithRels,
    BookPATCHOnPublication,
    TagAdd,
    GenresBooksAdd,
    BookPATCH,
)
from src.tasks.taskiq_tasks import async_render, async_delete_book
from src.schemas.books_authors import BookAuthorAdd

router = APIRouter(prefix="/author", tags=["Авторы и публикация книг"])


@router.post("/book")
async def add_book(
    data: BookAddWithAuthorsTagsGenres,
    db: DBDep,
    user_id: int = authorize_and_return_user_id(2),
):
    data.authors.append(user_id)
    book = await db.books.add(BookAdd(**data.model_dump()))
    data_to_add_m2m = [
        BookAuthorAdd(book_id=book.book_id, author_id=author) for author in data.authors
    ]
    data_to_tags_m2m = [
        TagAdd(book_id=book.book_id, title_tag=title) for title in data.tags
    ]
    data_to_genres_m2m = [
        GenresBooksAdd(book_id=book.book_id, genre_id=gen_id) for gen_id in data.genres
    ]
    await db.books_authors.add_bulk(data_to_add_m2m)
    await db.tags.add_bulk(data_to_tags_m2m)
    await db.books_genres.add_bulk(data_to_genres_m2m)
    await db.commit()
    return {"status": "OK", "data": book}


@router.get("/book")
async def get_book_by_id(book_id: int, db: DBDep):
    try:
        return await db.books.get_book_with_rels(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex


@router.patch("/book")
async def edit_bood_data(
    book_id: int,
    db: DBDep,
    data: BookPATCHWithRels,
    user_id: int = authorize_and_return_user_id(2),
):
    try:
        await db.books.get_one(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    await AuthService().verify_user_owns_book(
        user_id=user_id, book_id=book_id
    )  # Проверяем, владеет ли пользователь этой книгой
    book_patch_data = BookPATCH(
        **data.model_dump(exclude_unset=True)
    )  # Создаем pydantic-схему для будущего изменения данных

    # --- Изменение жанров и тегов ---
    genres = await db.books_genres.get_filtered(
        book_id=book_id
    )  # Получаем все жанры книги
    genres_ids_in_db = [genre.id for genre in genres]
    new_tags = data.genres
    same_els = set(genres_ids_in_db) & set(new_tags)
    genres_to_add = set(new_tags) - same_els
    genres_to_delete = set(genres_ids_in_db) - same_els
    data_to_add_genres = [
        GenresBooksAdd(genre_id=gen_book_id, book_id=book_id)
        for gen_book_id in genres_to_add
    ]

    # --- Изменение жанров внутри базы данных ---
    if genres_to_delete:
        await db.books_genres.delete_bulk_by_ids(genres_to_delete, book_id=book_id)
    if genres_to_add:
        await db.books_genres.add_bulk(data_to_add_genres)
    if book_patch_data.model_dump(exclude_unset=True):
        await db.books.edit(data=book_patch_data, is_patch=True, book_id=book_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/book")
async def delete_book(
    book_id: int, db: DBDep, s3: S3Dep, user_id: int = authorize_and_return_user_id(2)
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    try:
        book = await db.books.get_one(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    await async_delete_book.kiq(book_id=book_id)
    if book.is_rendered:
        await s3.books.delete_by_path(f"{book_id}/book.pdf")
    if book.cover_link:
        await s3.books.delete_by_path(f"{book_id}/preview.png")
    await db.books.delete(book_id=book_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/my_books")
async def get_my_books(
    db: DBDep,
    user_id: int = authorize_and_return_user_id(2),
):
    return await db.users.get_books_by_user(user_id=user_id)


# --- Обложки ---


@router.post("/cover")
async def add_cover(
    file: UploadFile,
    book_id: int,
    db: DBDep,
    s3: S3Dep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    cover_link = await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=cover_link),
        book_id=book_id,
    )
    await db.commit()
    return {"status": "OK"}


@router.put("/cover")
async def put_cover(
    file: UploadFile,
    book_id: int,
    db: DBDep,
    s3: S3Dep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    book = await db.books.get_one(book_id=book_id)
    if not book.cover_link:
        raise CoverNotFoundHTTPException
    await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=f"{book_id}/preview.png"),
        book_id=book_id,
    )
    await db.commit()
    return {"status": "OK"}


# --- Контент книги ---


@router.post("/content")
async def add_all_content(
    file: UploadFile,
    book_id: int,
    s3: S3Dep,
    db: DBDep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    if await s3.books.check_file_by_path(f"{book_id}/book.pdf"):
        raise ContentAlreadyExistsHTTPException
    await s3.books.save_content(book_id, file=file)
    await async_render.kiq(book_id=book_id)
    return {"status": "OK"}


@router.put("/content")
async def edit_content(
    book_id: int,
    content: UploadFile,
    s3: S3Dep,
    db: DBDep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    if not await s3.books.check_file_by_path(f"{book_id}/book.pdf"):
        raise ContentAlreadyExistsHTTPException
    await async_delete_book.kiq(book_id=book_id)
    await s3.books.save_content(book_id=book_id, file=content)
    await async_render.kiq(book_id=book_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/__test__")
async def test(role: UserRoleDep, user_id: int = authorize_and_return_user_id(2)):
    print("УСПЕШНО!")
    return {"status": "OK", "user_id": user_id}
