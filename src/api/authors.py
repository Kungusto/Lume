from fastapi import APIRouter, UploadFile
from src.services.auth import AuthService
from src.exceptions.books import (
    BookNotExistsOrYouNotOwnerException,
    BookNotExistsOrYouNotOwnerHTTPException,
    CoverNotFoundHTTPException,
    ContentAlreadyExistsHTTPException,
    BookNotFoundHTTPException,
    BookNotFoundException,
    CoverAlreadyExistsHTTPException,
    BookAlreadyPublicatedHTTPException,
    ContentNotFoundHTTPException,
    AuthorNotFoundException,
    AuthorNotFoundHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
)
from src.exceptions.files import (
    WrongFileExpensionException,
    WrongCoverResolutionException,
    WrongCoverResolutionHTTPException,
    WrongFileExpensionHTTPException,
)
from src.api.dependencies import S3Dep, DBDep, UserIdDep, UserRoleDep, ShouldCheckOwnerDep
from src.schemas.books import (
    BookAdd,
    BookAddWithAuthorsTagsGenres,
    BookPATCHWithRels,
    BookPATCHOnPublication,
    TagAdd,
    GenresBooksAdd,
    BookPATCH,
)
from src.exceptions.books import GenreNotFoundHTTPException, AuthorNotFoundHTTPException
from src.exceptions.base import ForeignKeyException
from src.tasks.tasks import render_book, delete_book_images, change_content
from src.schemas.books_authors import BookAuthorAdd
from src.models.books import BooksTagsORM
from src.validation.files import FileValidator
from src.utils.cache_manager import get_cache_manager
from src.services.books import BookService


router = APIRouter(prefix="/author", tags=["Авторы и публикация книг 📚"])
cache = get_cache_manager()


@router.post("/book")
async def add_book(
    db: DBDep,
    data: BookAddWithAuthorsTagsGenres,
    user_id: UserIdDep,
):
    try:
        book = await BookService(db=db).add_book(data=data, user_id=user_id)
    except AuthorNotFoundException as ex:
        raise AuthorNotFoundHTTPException from ex
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    return book


@router.patch("/book/{book_id}")
async def edit_book(
    db: DBDep,
    book_id: int,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    data: BookPATCHWithRels,
):
    try:
        await BookService(db=db).edit_book(
            book_id=book_id, user_id=user_id, user_role=user_role, data=data
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    return {"status": "OK"}


@router.delete("/book/{book_id}")
async def delete_book(
    book_id: int,
    db: DBDep,
    s3: S3Dep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
):
    if should_check_owner:
        await AuthService().verify_user_owns_book(
            user_id=user_id, book_id=book_id, db=db
        )
    try:
        book = await db.books.get_one(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    delete_book_images.delay(book_id)
    if book.is_rendered:
        await s3.books.delete_by_path(f"books/{book_id}/book.pdf")
    if book.cover_link:
        await s3.books.delete_by_path(f"books/{book_id}/preview.png")
    await db.pages.delete(book_id=book_id)
    await db.books.delete(book_id=book_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/my_books")
@cache.base()
async def get_my_books(
    db: DBDep,
    author_id: UserIdDep,
):
    return await db.users.get_books_by_user(user_id=author_id)


# --- Обложки ---


@router.post("/cover/{book_id}")
async def add_cover(
    file: UploadFile,
    book_id: int,
    db: DBDep,
    s3: S3Dep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
):
    if should_check_owner:
        await AuthService().verify_user_owns_book(
            user_id=user_id, book_id=book_id, db=db
        )
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
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
):
    if should_check_owner:
        await AuthService().verify_user_owns_book(
            user_id=user_id, book_id=book_id, db=db
        )
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
        data=BookPATCHOnPublication(cover_link=f"books/{book_id}/preview.png"),
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
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
):
    if should_check_owner:
        await AuthService().verify_user_owns_book(
            user_id=user_id, book_id=book_id, db=db
        )
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
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
):
    if should_check_owner:
        await AuthService().verify_user_owns_book(
            user_id=user_id, book_id=book_id, db=db
        )
    try:
        FileValidator.check_expansion_books(file_name=file.filename)
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    if not await s3.books.check_file_by_path(f"books/{book_id}/book.pdf"):
        raise ContentAlreadyExistsHTTPException
    await s3.books.save_content(book_id=book_id, file=file)
    await db.pages.delete(book_id=book_id)
    change_content.delay(book_id)
    await db.commit()
    return {"status": "OK"}


@router.post("/publicate/{book_id}")
async def publicate_book(
    book_id: int,
    db: DBDep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
):
    try:
        if should_check_owner:
            book = await AuthService().verify_user_owns_book(
                user_id=user_id, book_id=book_id, db=db
            )
        else:
            book = await db.books.get_one(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    if (not book.is_rendered) or (book.total_pages is None):
        raise ContentNotFoundHTTPException
    if book.cover_link is None:
        raise CoverNotFoundHTTPException
    if book.is_publicated:
        raise BookAlreadyPublicatedHTTPException
    data_to_update = BookPATCH(is_publicated=True)
    updated_data = await db.books.edit(
        data=data_to_update, is_patch=True, book_id=book_id
    )
    await db.commit()
    return updated_data
