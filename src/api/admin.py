from datetime import date
from fastapi import APIRouter, Body, Path
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
from src.docs_src.examples.admin import (
    add_genre_example,
    edit_tag_example,
    add_reason_example,
    ban_user_by_id_example,
    get_statements_by_date_example,
)
from src.docs_src.responses.admin import (
    add_genre_responses,
    add_reason_responses,
    add_tag_responses,
    ban_user_by_id_responses,
    change_role_responses,
    delete_genre_responses,
    delete_reason_responses,
    delete_tag_responses,
    edit_ban_date_responses,
    edit_genre_responses,
    edit_reason_responses,
    edit_tag_responses,
    generate_report_inside_app_responses,
    get_banned_users_responses,
    get_not_checked_reports_responses,
    get_statements_by_date_responses,
    mark_as_checked_responses,
    save_and_get_auto_statement_responses,
    unban_user_by_ban_id_responses,
)


router = APIRouter(prefix="/admin", tags=["Админ панель ⚜️"])


@router.patch(
    path="/{user_id}/change_role",
    summary="Изменение роли пользователя",
    description="Доступно только для ролей ADMIN и GENERAL_ADMIN",
    responses=change_role_responses,
)
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


@router.post(
    path="/genres",
    summary="Добавление жанра",
    description="Нельзя добавлять несколько одинаковых жанров. "
    "При добавлении, первая буква автоматически становится заглавной, "
    "а остальные - строчными",
    responses=add_genre_responses,
)
async def add_genre(
    db: DBDep,
    data: GenreAdd = Body(openapi_examples=add_genre_example),
):
    try:
        genre = await AdminService(db=db).add_genre(data=data)
    except GenreAlreadyExistsException as ex:
        raise GenreAlreadyExistsHTTPException from ex
    return genre


@router.put(
    path="/genres/{genre_id}",
    summary="Изменение названия жанра",
    responses=edit_genre_responses,
)
async def edit_genre(
    db: DBDep,
    data: GenreEdit = Body(openapi_examples=add_genre_example),
    genre_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).edit_genre(data=data, genre_id=genre_id)
    except GenreNotFoundException as ex:
        raise GenreNotFoundHTTPException from ex
    except GenreAlreadyExistsException as ex:
        raise GenreAlreadyExistsHTTPException from ex
    return {"status": "OK"}


@router.delete(
    path="/genres/{genre_id}",
    summary="Удаление жанра",
    description="Если на жанр ссылается хотя-бы одна книга, "
    "то удалить жанр будет невозможно. "
    "Это сделано во измежание случайного удаление множества книг",
    responses=delete_genre_responses,
)
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


@router.post(
    path="/tag", summary="Добавление тега к книге", responses=add_tag_responses
)
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


@router.delete(
    path="/tag/{tag_id}",
    summary="Удаление тега книги по его id",
    responses=delete_tag_responses,
)
async def delete_tag(
    db: DBDep,
    tag_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).delete_tag(tag_id=tag_id)
    except TagNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    return {"status": "OK"}


@router.put(
    path="/tag/{tag_id}", summary="Изменить тег книги", responses=edit_tag_responses
)
async def edit_tag(
    db: DBDep,
    data: TagEdit = Body(openapi_examples=edit_tag_example),
    tag_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).edit_tag(tag_id=tag_id, data=data)
    except TagNotFoundException as ex:
        raise TagNotFoundHTTPException from ex
    except TagAlreadyExistsException as ex:
        raise TagAlreadyExistsHTTPException from ex
    return {"status": "OK"}


@router.post(
    path="/reasons",
    summary="Добавить причину жалоб",
    description="Когда пользователь захочет пожаловаться на книгу, "
    "он должен будет указать причину жалобы",
    responses=add_reason_responses,
)
async def add_reason(
    db: DBDep,
    data: ReasonAdd = Body(openapi_examples=add_reason_example),
):
    try:
        reason = await AdminService(db=db).add_reason(data=data)
    except ReasonAlreadyExistsException as ex:
        raise ReasonAlreadyExistsHTTPException from ex
    return reason


@router.put(
    path="/reasons/{reason_id}",
    summary="Изменить названия причины бана",
    responses=edit_reason_responses,
)
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


@router.delete(
    path="/reasons/{reason_id}",
    summary="Удалить причину бана",
    description="Если есть хотя-бы одна не обработанная жалоба с этой причиной, "
    "удалить причину не получится",
    responses=delete_reason_responses,
)
async def delete_reason(
    db: DBDep,
    reason_id: int = Path(le=2**31),
):
    # FIXME: Обработка случая с ссылающимися жалобами на конкретную причину
    try:
        await AdminService(db=db).delete_reason(reason_id=reason_id)
    except ReasonNotFoundException as ex:
        raise ReasonNotFoundHTTPException from ex
    return {"status": "OK"}


@router.get(
    path="/reports",
    summary="Получить все не обработанные жалобы",
    responses=get_not_checked_reports_responses,
)
async def get_not_checked_reports(
    db: DBDep,
):
    return await AdminService(db=db).get_not_checked_reports()


@router.patch(
    path="/reports/{report_id}",
    summary='Отметить жалобу как "проверенную"',
    responses=mark_as_checked_responses,
)
async def mark_as_checked(
    db: DBDep,
    report_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).mark_as_checked(report_id=report_id)
    except ReportNotFoundException as ex:
        raise ReportNotFoundHTTPException from ex
    return {"status": "OK"}


@router.post(
    path="/ban/{user_id}",
    summary="Забанить пользователя до указанной даты",
    responses=ban_user_by_id_responses,
)
async def ban_user_by_id(
    db: DBDep,
    user_role: UserRoleDep,
    data: BanAddFromUser = Body(openapi_examples=ban_user_by_id_example),
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
        raise UserNotFoundHTTPException from ex
    return ban_data


@router.delete(
    path="/ban/{ban_id}",
    summary="Снятие бана с пользователя",
    description="<h2>❗ ВАЖНО ❗</h2> - снятие бана происходит по id бана, "
    "а не id пользователя",
    responses=unban_user_by_ban_id_responses,
)
async def unban_user_by_ban_id(
    db: DBDep,
    ban_id: int = Path(le=2**31),
):
    try:
        await AdminService(db=db).unban_user_by_id(ban_id=ban_id)
    except UserNotBannedException as ex:
        raise UserNotBannedHTTPException from ex
    return {"status": "OK"}


@router.put(
    path="/ban/{ban_id}",
    summary="Изменение сроков бана",
    responses=edit_ban_date_responses,
)
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


@router.get(
    path="/banned_users",
    summary="Получить всех забаненных пользователей",
    responses=get_banned_users_responses,
)
async def get_banned_users(db: DBDep):
    return await AdminService(db=db).get_banned_users()


@router.post(
    path="/statement",
    summary="Сгенерировать отчет",
    description="Путь сохранения подобных файлов указывается в "
    "параметре STATEMENT_DIR_PATH (.env)<br>"
    "Шаблон нейминга файлов: {STATEMENT_DIR_PATH}/users_{%Y-%m-%d_%H-%M-%S}.xlsx",
    responses=generate_report_inside_app_responses,
)
async def generate_report_inside_app(
    db: DBDep,
    s3: S3Dep,
    data: StatementRequestFromADMIN = Body(
        openapi_examples=get_statements_by_date_example
    ),
):
    return await AdminService(db=db, s3=s3).generate_report_inside_app(data=data)


@router.get(
    path="/statement",
    summary="Получить все сгенерированные отчеты в определенный день",
    description="Возвращает массив JSON-ов, содержащий путь в S3, а также URL доступа",
    responses=get_statements_by_date_responses,
)
async def get_statements_by_date(s3: S3Dep, statement_date: date):
    return await AdminService(s3=s3).get_statements_by_date(
        statement_date=statement_date
    )


@router.get(
    path="/statement/auto",
    summary="Сохранить в S3 отчеты, сгенерированные автоматически, и получить URL доступа",
    description="За автоматическую генерацию отвечает Celery beat. "
    "Он обновляет файл users_statement_auto каждые 5 минут",
    responses=save_and_get_auto_statement_responses,
)
async def save_and_get_auto_statement(s3: S3Dep):
    try:
        url = await AdminService(s3=s3).save_and_get_auto_statement()
    except StatementNotFoundException as ex:
        raise StatementNotFoundHTTPException from ex
    return url
