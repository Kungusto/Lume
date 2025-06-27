from fastapi import APIRouter, UploadFile
from src.services.auth import AuthService
from src.exceptions.books import (
    CoverNotFoundHTTPException,
    ContentAlreadyExistsHTTPException,
    BookNotFoundHTTPException,
    BookNotFoundException,
    CoverAlreadyExistsHTTPException,
    BookAlreadyPublicatedHTTPException,
)
from src.exceptions.files import (
    WrongFileExpensionException,
    WrongCoverResolutionException,
    WrongCoverResolutionHTTPException,
    WrongFileExpensionHTTPException,
)
from src.api.dependencies import S3Dep, DBDep, authorize_and_return_user_id
from src.schemas.books import (
    BookAdd,
    BookAddWithAuthorsTagsGenres,
    BookPATCHWithRels,
    BookPATCHOnPublication,
    TagAdd,
    GenresBooksAdd,
    BookPATCH,
)
from src.exceptions.books import GenreNotFoundHTTPException
from src.tasks.tasks import render_book, delete_book_images, change_content
from src.schemas.books_authors import BookAuthorAdd
from src.models.books import BooksTagsORM
from src.validation.files import FileValidator

router = APIRouter(prefix="/author", tags=["Авторы и публикация книг 📚"])


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


@router.get("/book/{book_id}")
async def get_book_by_id(book_id: int, db: DBDep):
    try:
        return await db.books.get_book_with_rels(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex


@router.patch("/book/{book_id}")
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
        user_id=user_id, book_id=book_id, db=db
    )  # Проверяем, владеет ли пользователь этой книгой
    book_patch_data = BookPATCH(
        **data.model_dump(exclude_unset=True)
    )  # Создаем pydantic-схему для будущего изменения данных

    # --- Изменение жанров и тегов ---
    genres = await db.books_genres.get_filtered(
        book_id=book_id
    )  # Получаем все жанры книги
    tags = await db.tags.get_filtered(book_id=book_id)
    genres_ids_in_db = [genre.genre_id for genre in genres]
    tags_titles_in_db = [tag.title_tag for tag in tags]
    # Вычисление нужных и НЕ нужных нам жанров
    all_genres = await db.genres.get_all()
    all_ids = [genre.genre_id for genre in all_genres]
    for input_genre in data.genres:
        if input_genre not in all_ids:
            raise GenreNotFoundHTTPException
    new_genres = data.genres or set()
    same_els_genres = set(genres_ids_in_db) & set(new_genres)
    genres_to_add = set(new_genres) - same_els_genres
    genres_to_delete = set(genres_ids_in_db) - same_els_genres
    # Вычисление нужных и НЕ нужных нам тегов
    new_tags = data.tags or set()
    same_els_tags = set(tags_titles_in_db) & set(new_tags)
    tags_to_add = set(new_tags) - same_els_tags
    tags_to_delete = set(tags_titles_in_db) - same_els_tags

    data_to_add_genres = [
        GenresBooksAdd(genre_id=gen_book_id, book_id=book_id)
        for gen_book_id in genres_to_add
    ]

    data_to_add_tags = [
        TagAdd(title_tag=tag_book_title, book_id=book_id)
        for tag_book_title in tags_to_add
    ]

    # --- Изменение жанров внутри базы данных ---
    if genres_to_delete:
        await db.books_genres.delete_bulk_by_ids(genres_to_delete, book_id=book_id)
    if genres_to_add:
        await db.books_genres.add_bulk(data_to_add_genres)
    if tags_to_delete:
        await db.tags.delete(
            BooksTagsORM.title_tag.in_(tags_to_delete), book_id=book_id
        )
    if tags_to_add:
        await db.tags.add_bulk(data_to_add_tags)
    if book_patch_data.model_dump(exclude_unset=True):
        await db.books.edit(data=book_patch_data, is_patch=True, book_id=book_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/book/{book_id}")
async def delete_book(
    book_id: int, db: DBDep, s3: S3Dep, user_id: int = authorize_and_return_user_id(2)
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    try:
        book = await db.books.get_one(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    delete_book_images.delay(book_id)
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


@router.post("/cover/{book_id}")
async def add_cover(
    file: UploadFile,
    book_id: int,
    db: DBDep,
    s3: S3Dep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    try:
        FileValidator.check_expansion_images(file_name=file.filename)
        await FileValidator.validate_cover(file_img=file)
    except WrongCoverResolutionException as ex:
        raise WrongCoverResolutionHTTPException from ex
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    book = await db.books.get_one(book_id=book_id)
    if book.cover_link is not None:
        raise CoverAlreadyExistsHTTPException
    cover_link = await s3.books.save_cover(file=file, book_id=book_id)
    await db.books.edit(
        is_patch=True,
        data=BookPATCHOnPublication(cover_link=cover_link),
        book_id=book_id,
    )
    await db.commit()
    return {"status": "OK"}


@router.put("/cover/{book_id}")
async def put_cover(
    file: UploadFile,
    book_id: int,
    db: DBDep,
    s3: S3Dep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    try:
        FileValidator.check_expansion_images(file_name=file.filename)
        await FileValidator.validate_cover(file_img=file)
    except WrongCoverResolutionException as ex:
        raise WrongCoverResolutionHTTPException from ex
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
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


@router.post("/content/{book_id}")
async def add_all_content(
    file: UploadFile,
    book_id: int,
    s3: S3Dep,
    db: DBDep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    try:
        FileValidator.check_expansion_books(file_name=file.filename)
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    if await s3.books.check_file_by_path(f"books/{book_id}/book.pdf"):
        raise ContentAlreadyExistsHTTPException
    await s3.books.save_content(book_id, file=file)
    render_book.delay(book_id)
    return {"status": "OK"}


@router.put("/content/{book_id}")
async def edit_content(
    book_id: int,
    file: UploadFile,
    s3: S3Dep,
    db: DBDep,
    user_id: int = authorize_and_return_user_id(2),
):
    await AuthService().verify_user_owns_book(user_id=user_id, book_id=book_id, db=db)
    try:
        FileValidator.check_expansion_books(file_name=file.filename)
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    if not await s3.books.check_file_by_path(f"books/{book_id}/book.pdf"):
        raise ContentAlreadyExistsHTTPException
    await s3.books.save_content(book_id=book_id, file=file)
    change_content.delay(book_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/book/{page_number}")
async def page_number(page_number: int):
    return {"status": "OK", "page_number": page_number}


@router.post("/publicate/{book_id}")
async def publicate_book(
    book_id: int, db: DBDep, user_id: int = authorize_and_return_user_id(2)
):
    try:
        book = await AuthService().verify_user_owns_book(
            user_id=user_id, book_id=book_id, db=db
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    if book.is_publicated:
        raise BookAlreadyPublicatedHTTPException
    data_to_update = BookPATCH(is_publicated=True)
    updated_data = await db.books.edit(
        data=data_to_update, is_patch=True, book_id=book_id
    )
    await db.commit()
    return updated_data
