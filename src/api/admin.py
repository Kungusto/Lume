from fastapi import APIRouter, Path
from src.api.dependencies import authorize_and_return_user_id, DBDep
from src.schemas.users import UserRolePUT
from src.schemas.books import GenreAdd, GenreEdit, TagAdd, TagEdit
from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.exceptions.books import (
    GenreAlreadyExistsHTTPException,
    GenreNotFoundHTTPException,
    TagNotFoundHTTPException,
    BookNotFoundHTTPException,
)


router = APIRouter(prefix="/admin", tags=["Админ панель ⚜️"])


@router.patch("/{user_id}/change_role")
async def change_role(
    db: DBDep,
    data: UserRolePUT,
    user_id: int = Path(le=2**31),
):
    await db.users.edit(data=data, user_id=user_id)
    await db.commit()
    return {"status": "OK"}


@router.post("/genres")
async def add_genre(
    db: DBDep,
    data: GenreAdd,
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        genre = await db.genres.add(data=data)
    except AlreadyExistsException as ex:
        raise GenreAlreadyExistsHTTPException from ex
    await db.commit()
    return genre


@router.put("/genres/{genre_id}")
async def edit_genre(
    db: DBDep,
    data: GenreEdit,
    genre_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.genres.get_one(genre_id=genre_id)
    except ObjectNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    edit_genre = await db.genres.edit(data=data, genre_id=genre_id)
    await db.commit()
    return {"status": "OK", "data": edit_genre}


@router.delete("/genres/{genre_id}")
async def delete_genre(
    db: DBDep,
    genre_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.genres.get_one(genre_id=genre_id)
    except ObjectNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    await db.genres.delete(genre_id=genre_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/tag/{tag_id}")
async def delete_tag(
    db: DBDep,
    tag_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.tags.get_one(id=tag_id)
    except ObjectNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    await db.tags.delete(id=tag_id)
    await db.commit()
    return {"status": "OK"}


@router.post("/tag")
async def add_tag(
    db: DBDep,
    data: TagAdd,
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.books.get_one(book_id=data.book_id)
    except ObjectNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    await db.tags.add(data=data)
    await db.commit()
    return {"status": "OK"}


@router.put("/tag/{tag_id}")
async def edit_tag(
    db: DBDep,
    data: TagEdit,
    tag_id: int = Path(le=2**31),
):
    try:
        await db.tags.get_one(id=tag_id)
    except ObjectNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    await db.tags.edit(data=data, id=tag_id)
    await db.commit()
    return {"status": "OK"}
