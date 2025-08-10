from fastapi import APIRouter, Body, Path, UploadFile
from src.exceptions.books import (
    BookAlreadyPublicatedException,
    BookNotExistsOrYouNotOwnerException,
    BookNotExistsOrYouNotOwnerHTTPException,
    ContentAlreadyExistsException,
    ContentNotFoundException,
    CoverAlreadyExistsException,
    CoverNotFoundException,
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
from src.api.dependencies import (
    S3Dep,
    DBDep,
    UserIdDep,
    UserRoleDep,
    ShouldCheckOwnerDep,
)
from src.schemas.books import (
    BookAddWithAuthorsTagsGenres,
    BookPATCHWithRels,
)
from src.utils.cache_manager import get_cache_manager
from src.services.authors import AuthorsService
from src.docs_src.examples.authors import add_book_example, book_patch_examples
from src.docs_src.responses.authors import (
    add_book_responses,
    add_all_content_responses,
    add_cover_responses,
    delete_book_responses,
    edit_book_responses,
    edit_content_responses,
    get_my_books_responses,
    publicate_book_responses,
    put_cover_responses,
    get_publication_status_responses,
)
from src.constants.files import AllowedExtensions


router = APIRouter(prefix="/author", tags=["Авторы и публикация книг 📚"])
cache = get_cache_manager()


@router.post(
    path="/book",
    summary="Публикация книги от имени автора",
    description="Книги могут публиковать все, кроме обычных пользователей",
    responses=add_book_responses,
)
async def add_book(
    db: DBDep,
    user_id: UserIdDep,
    data: BookAddWithAuthorsTagsGenres = Body(openapi_examples=add_book_example),
):
    try:
        book = await AuthorsService(db=db).add_book(data=data, user_id=user_id)
    except AuthorNotFoundException as ex:
        raise AuthorNotFoundHTTPException from ex
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    return book


@router.patch(
    path="/book/{book_id}",
    summary="Изменение данных о книге",
    description="AUTHOR может изменить только свою книгу, "
    "ADMIN и GENERAL_ADMIN может изменять любые книги",
    responses=edit_book_responses,
)
async def edit_book(
    db: DBDep,
    user_id: UserIdDep,
    user_role: UserRoleDep,
    book_id: int = Path(le=2**31),
    data: BookPATCHWithRels = Body(openapi_examples=book_patch_examples),
):
    try:
        await AuthorsService(db=db).edit_book(
            book_id=book_id, user_id=user_id, user_role=user_role, data=data
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    return {"status": "OK"}


@router.delete(
    path="/book/{book_id}",
    summary="Удаление книги",
    description="AUTHOR может удалить только свою книгу, "
    "ADMIN и GENERAL_ADMIN может удалять любые книги",
    responses=delete_book_responses,
)
async def delete_book(
    db: DBDep,
    s3: S3Dep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
    book_id: int = Path(le=2**31),
):
    try:
        await AuthorsService(db=db, s3=s3).delete_book(
            should_check_owner=should_check_owner,
            book_id=book_id,
            user_id=user_id,
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    return {"status": "OK"}


@router.get(
    path="/my_books",
    summary="Получение своих книг",
    description="Возвращает список книг с подробностями о них",
    responses=get_my_books_responses,
)
@cache.base()
async def get_my_books(
    db: DBDep,
    author_id: UserIdDep,
):
    return await AuthorsService(db=db).get_my_books(author_id=author_id)


# --- Обложки ---


@router.post(
    path="/cover/{book_id}",
    summary="Добавление обложки",
    description=f"Поддерживаемые расширения: {', '.join(AllowedExtensions.IMAGES)}",
    responses=add_cover_responses,
)
async def add_cover(
    db: DBDep,
    s3: S3Dep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
    file: UploadFile,
    book_id: int = Path(le=2**31),
):
    try:
        await AuthorsService(db=db, s3=s3).add_cover(
            should_check_owner=should_check_owner,
            book_id=book_id,
            user_id=user_id,
            file=file,
        )
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    except WrongCoverResolutionException as ex:
        raise WrongCoverResolutionHTTPException from ex
    except CoverAlreadyExistsException as ex:
        raise CoverAlreadyExistsHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    return {"status": "OK"}


@router.put(
    path="/cover/{book_id}",
    summary="Изменить уже добавленную обложку",
    description=f"Поддерживаемые расширения: {', '.join(AllowedExtensions.IMAGES)}",
    responses=put_cover_responses,
)
async def put_cover(
    file: UploadFile,
    db: DBDep,
    s3: S3Dep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
    book_id: int = Path(le=2**31),
):
    try:
        await AuthorsService(db=db, s3=s3).put_cover(
            should_check_owner=should_check_owner,
            book_id=book_id,
            user_id=user_id,
            file=file,
        )
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    except WrongCoverResolutionException as ex:
        raise WrongCoverResolutionHTTPException from ex
    except CoverNotFoundException as ex:
        raise CoverNotFoundHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    return {"status": "OK"}


# --- Контент книги ---


@router.post(
    path="/content/{book_id}",
    summary="Опубликовать контент книги",
    description=f"Поддерживаемые форматы: {AllowedExtensions.BOOKS}",
    responses=add_all_content_responses,
)
async def add_all_content(
    s3: S3Dep,
    db: DBDep,
    file: UploadFile,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
    book_id: int = Path(le=2**31),
):
    try:
        await AuthorsService(db=db, s3=s3).add_all_content(
            should_check_owner=should_check_owner,
            user_id=user_id,
            book_id=book_id,
            file=file,
        )
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    except ContentAlreadyExistsException as ex:
        raise ContentAlreadyExistsHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    return {"status": "OK"}


@router.put(
    path="/content/{book_id}",
    summary="Изменить уже опубликованный контент",
    description=f"Поддерживаемые форматы: {AllowedExtensions.BOOKS}",
    responses=edit_content_responses,
)
async def edit_content(
    file: UploadFile,
    s3: S3Dep,
    db: DBDep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
    book_id: int = Path(le=2**31),
):
    try:
        await AuthorsService(db=db, s3=s3).edit_content(
            should_check_owner=should_check_owner,
            user_id=user_id,
            book_id=book_id,
            file=file,
        )
    except WrongFileExpensionException as ex:
        raise WrongFileExpensionHTTPException from ex
    except ContentNotFoundException as ex:
        raise ContentNotFoundHTTPException from ex
    except BookNotExistsOrYouNotOwnerException as ex:
        raise BookNotExistsOrYouNotOwnerHTTPException from ex
    return {"status": "OK"}


@router.post(
    path="/publicate/{book_id}",
    summary="Опубликовать книгу",
    description="После того как она будет опубликована, пользователи смогут "
    "её видеть в результатах главного поиска. Для того чтобы опубликовать книгу, она должна "
    "иметь обложку и контент",
    responses=publicate_book_responses,
)
async def publicate_book(
    db: DBDep,
    user_id: UserIdDep,
    should_check_owner: ShouldCheckOwnerDep,
    book_id: int = Path(le=2**31),
):
    try:
        await AuthorsService(db=db).publicate_book(
            book_id=book_id,
            user_id=user_id,
            should_check_owner=should_check_owner,
        )
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    except ContentNotFoundException as ex:
        raise ContentNotFoundHTTPException from ex
    except CoverNotFoundException as ex:
        raise CoverNotFoundHTTPException from ex
    except BookAlreadyPublicatedException as ex:
        raise BookAlreadyPublicatedHTTPException from ex
    return {"status": "OK"}


@router.get(
    path="/{book_id}/publication_status",
    summary="Посмотреть статус публикации книги",
    description="Статусы публикации: uploaded, rendering, ready, failed",
    responses=get_publication_status_responses,
)
async def get_status_publicate_book(
    db: DBDep,
    book_id: int = Path(le=2**31),
):
    try:
        return await db.books.get_render_status(book_id=book_id)
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex