from datetime import date, datetime, timezone
from fastapi import APIRouter, Path
from src.api.dependencies import S3Dep, authorize_and_return_user_id, DBDep, UserRoleDep
from src.schemas.users import UserRolePUT
from src.schemas.books import GenreAdd, GenreEdit, TagAdd, TagEdit
from src.schemas.reports import ReasonAdd, ReasonEdit, BanAdd, BanAddFromUser, BanEdit
from src.models.reports import BanORM
from src.exceptions.base import AlreadyExistsException, ObjectNotFoundException
from src.exceptions.books import (
    GenreAlreadyExistsHTTPException,
    GenreNotFoundHTTPException,
    TagNotFoundHTTPException,
    BookNotFoundHTTPException,
    TagAlreadyExistsHTTPException,
)
from src.exceptions.auth import (
    UserNotFoundHTTPException,
    ChangePermissionsOfADMINHTTPException,
)
from src.exceptions.reports import (
    ReasonAlreadyExistsHTTPException,
    ReasonNotFoundHTTPException,
    AlreadyBannedHTTPException,
    UserNotBannedHTTPException,
)
from src.repositories.database.utils import AnalyticsQueryFactory
from src.schemas.analytics import (
    UsersStatement,
    UsersStatementWithoutDate,
    StatementRequestFromADMIN,
)

from src.analytics.excel.active_users import UsersDFExcelRepository
from src.exceptions.files import StatementNotFoundHTTPException


router = APIRouter(prefix="/admin", tags=["Админ панель ⚜️"])


@router.patch("/{user_id}/change_role")
async def change_role(
    db: DBDep,
    data: UserRolePUT,
    current_user_role: UserRoleDep,
    admin_id: int = authorize_and_return_user_id(3),
    user_id: int = Path(le=2**31),
):
    try:
        user = await db.users.get_one(user_id=user_id)
    except ObjectNotFoundException as ex:
        raise UserNotFoundHTTPException from ex

    # На случай если админ решит понизить другого админа
    if current_user_role == user.role:
        raise ChangePermissionsOfADMINHTTPException
    if user.role == "GENERAL_ADMIN":
        raise ChangePermissionsOfADMINHTTPException

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
    await db.genres.edit(data=data, genre_id=genre_id)
    await db.commit()
    return {"status": "OK"}


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
    if await db.tags.get_filtered(book_id=data.book_id, title_tag=data.title_tag):
        raise TagAlreadyExistsHTTPException
    await db.tags.add(data=data)
    await db.commit()
    return {"status": "OK"}


@router.put("/tag/{tag_id}")
async def edit_tag(
    db: DBDep,
    data: TagEdit,
    tag_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.tags.get_one(id=tag_id)
    except ObjectNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    await db.tags.edit(data=data, id=tag_id)
    await db.commit()
    return {"status": "OK"}


@router.post("/reasons")
async def add_reason(
    db: DBDep,
    data: ReasonAdd,
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        reason = await db.reasons.add(data)
    except AlreadyExistsException as ex:
        raise ReasonAlreadyExistsHTTPException from ex
    await db.commit()
    return reason


@router.put("/reasons/{reason_id}")
async def edit_reason(
    db: DBDep,
    data: ReasonEdit,
    reason_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.reasons.get_one(reason_id=reason_id)
    except ObjectNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    await db.reasons.edit(data=data, reason_id=reason_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/reasons/{reason_id}")
async def delete_reason(
    db: DBDep,
    reason_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    try:
        await db.reasons.get_one(reason_id=reason_id)
    except ObjectNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    await db.reasons.delete(reason_id=reason_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/reports")
async def get_not_checked_reports(
    db: DBDep,
    user_id: int = authorize_and_return_user_id(3),
):
    return await db.reports.get_filtered(is_checked=False)


@router.patch("/reports/{report_id}")
async def mark_as_checked(
    db: DBDep,
    report_id: int = Path(le=2**31),
    user_id: int = authorize_and_return_user_id(3),
):
    await db.reports.mark_as_checked(report_id=report_id)
    await db.commit()
    return {"status": "OK"}


@router.post("/ban/{user_id}")
async def ban_user_by_id(
    db: DBDep,
    data: BanAddFromUser,
    user_role: UserRoleDep,
    user_id: int = Path(le=2**31),
    admin_id: int = authorize_and_return_user_id(3),
):
    try:
        user = await db.users.get_one(user_id=user_id)
    except ObjectNotFoundException as ex:
        raise UserNotFoundHTTPException from ex
    if await db.bans.get_filtered(
        BanORM.ban_until > datetime.now(timezone.utc), user_id=user_id
    ):
        raise AlreadyBannedHTTPException
    if user_role == user.role.value:
        raise ChangePermissionsOfADMINHTTPException
    if user.role.value == "GENERAL_ADMIN":
        raise ChangePermissionsOfADMINHTTPException
    # На случай если админ решит понизить другого админа
    ban_data = await db.bans.add(data=BanAdd(**data.model_dump(), user_id=user_id))
    await db.commit()
    return ban_data


@router.delete("/ban/{ban_id}")
async def unban_user_by_ban_id(
    db: DBDep,
    ban_id: int = Path(le=2**31),
    admin_id: int = authorize_and_return_user_id(3),
):
    if not await db.bans.get_filtered(ban_id=ban_id):
        raise UserNotBannedHTTPException
    await db.bans.delete(ban_id=ban_id)
    await db.commit()
    return {"status": "OK"}


@router.put("/ban/{ban_id}")
async def edit_ban_date(
    db: DBDep,
    data: BanEdit,
    ban_id: int = Path(le=2**31),
    admin_id: int = authorize_and_return_user_id(3),
):
    if not await db.bans.get_filtered(ban_id=ban_id):
        raise UserNotBannedHTTPException
    await db.bans.edit(data=data, ban_id=ban_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/banned_users")
async def get_banned_users(
    db: DBDep,
    admin_id: int = authorize_and_return_user_id(3),
):
    return await db.bans.get_banned_users()


@router.post("/statement")
async def generate_report_inside_app(
    db: DBDep, data: StatementRequestFromADMIN, s3: S3Dep
):
    interval = data.interval
    now = datetime.now()
    date_template = "%Y-%m-%d_%H-%M-%S"
    analytics_query = AnalyticsQueryFactory.users_data_sql(
        now=now, interval_td=interval
    )
    model = await db.session.execute(analytics_query)
    data = UsersStatementWithoutDate.model_validate(model.first(), from_attributes=True)
    result = UsersStatement(
        **data.model_dump(),
        started_date_as_str=(now - interval).strftime(date_template),
        ended_date_as_str=now.strftime(date_template),
    )
    excel_doc = UsersDFExcelRepository(
        f"src/analytics/data/users_{now.strftime(date_template)}.xlsx"
    )
    excel_doc.add(result)
    excel_doc.commit()
    excel_bytes = excel_doc.to_bytes()
    await s3.analytics.save_statement(
        key=f"analytics/{now.strftime('%Y-%m-%d')}/users_{now.strftime(date_template)}.xlsx",
        body=excel_bytes,
    )
    return result


@router.get("/statement")
async def get_statements_by_date(s3: S3Dep, statement_date: date):
    statemenets = await s3.analytics.list_objects_by_prefix(
        f"analytics/{statement_date.strftime('%Y-%m-%d')}"
    )
    urls = []
    for statement in statemenets:
        key_url = await s3.analytics.generate_url(file_path=statement)
        urls.append({"key": statement, "url": key_url})
    return urls


@router.get("/statement/auto")
async def save_and_get_auto_statement(s3: S3Dep):
    key = f"analytics/auto/{datetime.today().strftime('%Y-%m-%d_%H-%M')}"
    try:
        with open("src/analytics/data/users_statement_auto.xlsx", "rb") as doc:
            content = doc.read()
            if not content:
                raise StatementNotFoundHTTPException
            doc.seek(0)
            await s3.analytics.save_statement(key=key, body=doc)
    except FileNotFoundError as ex:
        raise StatementNotFoundHTTPException from ex
    # делаем файл пустым
    with open("src/analytics/data/users_statement_auto.xlsx", "w") as f:
        f.truncate(0)
    return await s3.analytics.generate_url(file_path=key)
