from datetime import date
from fastapi import APIRouter, Path
from src.api.dependencies import S3Dep, DBDep, UserRoleDep
from src.schemas.users import UserRolePUT
from src.schemas.books import GenreAdd, GenreEdit, TagAdd, TagEdit
from src.schemas.reports import ReasonAdd, ReasonEdit, BanAddFromUser, BanEdit
from src.exceptions.books import (
    BookNotFoundException,
    CannotDeleteGenreException,
    CannotDeleteGenreHTTPException,
    GenreAlreadyExistsException,
    GenreAlreadyExistsHTTPException,
    GenreNotFoundException,
    GenreNotFoundHTTPException,
    TagAlreadyExistsException,
    TagNotFoundException,
    TagNotFoundHTTPException,
    BookNotFoundHTTPException,
    TagAlreadyExistsHTTPException,
)
from src.exceptions.auth import (
    ChangePermissionsOfADMINException,
    UserNotFoundException,
    UserNotFoundHTTPException,
    ChangePermissionsOfADMINHTTPException,
)
from src.exceptions.reports import (
    AlreadyBannedException,
    ReasonAlreadyExistsException,
    ReasonAlreadyExistsHTTPException,
    ReasonNotFoundException,
    ReasonNotFoundHTTPException,
    AlreadyBannedHTTPException,
    ReportNotFoundException,
    ReportNotFoundHTTPException,
    UserNotBannedException,
    UserNotBannedHTTPException,
)
from src.schemas.analytics import (
    StatementRequestFromADMIN,
)

from src.exceptions.files import (
    StatementNotFoundException,
    StatementNotFoundHTTPException,
)
from src.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["Админ панель ⚜️"])


@router.patch("/{user_id}/change_role")
async def change_role(
    db: DBDep,
    data: UserRolePUT,
    current_user_role: UserRoleDep,
    user_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).change_role(
            data=data,
            current_user_role=current_user_role,
            user_id=user_id,
        )
    except UserNotFoundException as ex:
        raise UserNotFoundHTTPException from ex
    except ChangePermissionsOfADMINException as ex:
        raise ChangePermissionsOfADMINHTTPException from ex
    return {"status": "OK"}


@router.post("/genres")
async def add_genre(
    db: DBDep,
    data: GenreAdd,
):
    try:
        genre = await AdminService(db=db).add_genre(data=data)
    except GenreAlreadyExistsException as ex:
        raise GenreAlreadyExistsHTTPException from ex
    return genre


@router.put("/genres/{genre_id}")
async def edit_genre(
    db: DBDep,
    data: GenreEdit,
    genre_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).edit_genre(data=data, genre_id=genre_id)
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    except GenreAlreadyExistsException as ex:
        raise GenreAlreadyExistsHTTPException from ex
    return {"status": "OK"}


@router.delete("/genres/{genre_id}")
async def delete_genre(
    db: DBDep,
    genre_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).delete_genre(genre_id=genre_id)
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    except CannotDeleteGenreException as ex:
        raise CannotDeleteGenreHTTPException from ex
    return {"status": "OK"}


@router.post("/tag")
async def add_tag(
    db: DBDep,
    data: TagAdd,
):
    try:
        tag = await AdminService(db=db).add_tag(data=data)
    except TagAlreadyExistsException as ex:
        raise TagAlreadyExistsHTTPException from ex
    except BookNotFoundException as ex:
        raise BookNotFoundHTTPException from ex
    return tag


@router.delete("/tag/{tag_id}")
async def delete_tag(
    db: DBDep,
    tag_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).delete_tag(tag_id=tag_id)
    except TagNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    return {"status": "OK"}


@router.put("/tag/{tag_id}")
async def edit_tag(
    db: DBDep,
    data: TagEdit,
    tag_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).edit_tag(tag_id=tag_id, data=data)
    except TagNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    except TagAlreadyExistsException as ex:
        raise TagAlreadyExistsHTTPException from ex
    return {"status": "OK"}


@router.post("/reasons")
async def add_reason(
    db: DBDep,
    data: ReasonAdd,
):
    try:
        reason = await AdminService(db=db).add_reason(data=data)
    except ReasonAlreadyExistsException as ex:
        raise ReasonAlreadyExistsHTTPException from ex
    return reason


@router.put("/reasons/{reason_id}")
async def edit_reason(
    db: DBDep,
    data: ReasonEdit,
    reason_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).edit_reason(reason_id=reason_id, data=data)
    except ReasonNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    except ReasonAlreadyExistsException as ex:
        raise ReasonAlreadyExistsHTTPException from ex
    return {"status": "OK"}


@router.delete("/reasons/{reason_id}")
async def delete_reason(
    db: DBDep,
    reason_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).delete_reason(reason_id=reason_id)
    except ReasonNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    return {"status": "OK"}


@router.get("/reports")
async def get_not_checked_reports(
    db: DBDep,
):
    return await AdminService(db=db).get_not_checked_reports()


@router.patch("/reports/{report_id}")
async def mark_as_checked(
    db: DBDep,
    report_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).mark_as_checked(report_id=report_id)
    except ReportNotFoundException as ex:
        raise ReportNotFoundHTTPException from ex
    return {"status": "OK"}


@router.post("/ban/{user_id}")
async def ban_user_by_id(
    db: DBDep,
    data: BanAddFromUser,
    user_role: UserRoleDep,
    user_id: int = Path(le=2**31),
):
    try:
        ban_data = await AdminService(db=db).ban_user_by_id(
            data=data,
            user_role=user_role,
            user_id=user_id,
        )
    except AlreadyBannedException as ex:
        raise AlreadyBannedHTTPException from ex
    except ChangePermissionsOfADMINException as ex:
        raise ChangePermissionsOfADMINHTTPException from ex
    except UserNotFoundException as ex:
        raise UserNotBannedHTTPException from ex
    return ban_data


@router.delete("/ban/{ban_id}")
async def unban_user_by_ban_id(
    db: DBDep,
    ban_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).unban_user_by_id(ban_id=ban_id)
    except UserNotBannedException as ex:
        raise UserNotBannedHTTPException from ex
    return {"status": "OK"}


@router.put("/ban/{ban_id}")
async def edit_ban_date(
    db: DBDep,
    data: BanEdit,
    ban_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).edit_ban_date(ban_id=ban_id, data=data)
    except UserNotBannedException as ex:
        raise UserNotBannedHTTPException from ex
    return {"status": "OK"}


@router.get("/banned_users")
async def get_banned_users(db: DBDep):
    return await AdminService(db=db).get_banned_users()


@router.post("/statement")
async def generate_report_inside_app(
    db: DBDep, data: StatementRequestFromADMIN, s3: S3Dep
):
    return await AdminService(db=db, s3=s3).generate_report_inside_app(data=data)


@router.get("/statement")
async def get_statements_by_date(s3: S3Dep, statement_date: date):
    return await AdminService(s3=s3).get_statements_by_date(
        statement_date=statement_date
    )


@router.get("/statement/auto")
async def save_and_get_auto_statement(s3: S3Dep):
    try:
        url = await AdminService(s3=s3).save_and_get_auto_statement()
    except StatementNotFoundException as ex:
        raise StatementNotFoundHTTPException from ex
    return url
