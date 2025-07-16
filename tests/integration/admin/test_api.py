"""
Запустить этот файл отдельно:
pytest -s -v tests/integration/admin/test_api.py
"""

from datetime import date
from pathlib import Path
from src.tasks.tasks import auto_statement
from src.config import settings


async def test_change_user_role(auth_new_second_admin, new_user, new_general_admin):
    # изменить роль несуществующему пользователю
    response_change_role_non_existent_user = await auth_new_second_admin.patch(
        url="admin/9999/change_role", json={"role": "AUTHOR"}
    )
    assert response_change_role_non_existent_user.status_code == 404

    # изменить роль главного админа на обычного пользователя
    response_change_role_to_general_admin = await auth_new_second_admin.patch(
        url=f"admin/{new_general_admin.user_id}/change_role", json={"role": "USER"}
    )
    assert response_change_role_to_general_admin.status_code == 403

    # изменить роль пользователя на админа
    response_change_role = await auth_new_second_admin.patch(
        url=f"admin/{new_user.user_id}/change_role", json={"role": "ADMIN"}
    )
    assert response_change_role.status_code == 200

    # изменить роль пользователя, ставшего админом
    response_change_role = await auth_new_second_admin.patch(
        url=f"admin/{new_user.user_id}/change_role", json={"role": "USER"}
    )
    assert response_change_role.status_code == 403


async def test_add_already_exist_genre(auth_new_second_admin, new_genre):
    response_add_already_exist_genre = await auth_new_second_admin.post(
        "/admin/genres", json={"title": new_genre.title}
    )
    assert response_add_already_exist_genre.status_code == 409


async def test_add_genre(auth_new_second_admin):
    response_add_genre = await auth_new_second_admin.post(
        "/admin/genres", json={"title": "Страшилки!"}
    )
    assert response_add_genre.status_code == 200


async def test_edit_genre(db, auth_new_second_admin, new_genre):
    update_data = {"title": "Роман_"}
    response_edit_genre = await auth_new_second_admin.put(
        f"/admin/genres/{new_genre.genre_id}", json=update_data
    )
    assert response_edit_genre.status_code == 200
    db_genre = await db.genres.get_one(genre_id=new_genre.genre_id)
    assert db_genre.title == update_data.get("title", None)

    response_edit_genre = await auth_new_second_admin.put(
        "/admin/genres/9999", json={"title": "Изменяю несуществующий жанр!"}
    )
    assert response_edit_genre.status_code == 404


async def test_delete_genre(db, auth_new_second_admin, new_genre):
    # 200 OK
    response_delete_genre = await auth_new_second_admin.delete(
        f"/admin/genres/{new_genre.genre_id}"
    )
    assert response_delete_genre.status_code == 200
    assert not await db.genres.get_filtered(genre_id=new_genre.genre_id)

    # Пробуем удалить несуществующий жанр
    response_delete_genre = await auth_new_second_admin.delete("/admin/genres/9999")
    assert response_delete_genre.status_code == 404


async def test_delete_tag(db, auth_new_second_admin, new_tag):
    # 200 OK
    response_delete_tag = await auth_new_second_admin.delete(
        url=f"admin/tag/{new_tag.id}"
    )
    assert response_delete_tag.status_code == 200
    assert not await db.tags.get_filtered(id=new_tag.id)

    # Пробуем удалить несуществующий тег
    response_delete_non_existent_tag = await auth_new_second_admin.delete(
        url="admin/tag/9999"
    )
    assert response_delete_non_existent_tag.status_code == 404


async def test_add_tag(db, auth_new_second_admin, new_book):
    # 200 OK
    data_to_add = {"book_id": new_book.book_id, "title_tag": "Много роз!"}
    response_add_tag = await auth_new_second_admin.post(
        url="admin/tag", json=data_to_add
    )
    assert response_add_tag.status_code == 200
    assert await db.tags.get_filtered(
        book_id=new_book.book_id, title_tag=data_to_add.get("title_tag", None)
    )

    # Пробуем тот же самый тег, к той же самой книге
    response_add_tag = await auth_new_second_admin.post(
        url="admin/tag", json=data_to_add
    )
    assert response_add_tag.status_code == 409

    # Пробуем добавить тег к несуществующей книге
    wrong_data_to_add = {"book_id": 9999, "title_tag": "Много роз!"}
    response_add_tag = await auth_new_second_admin.post(
        url="admin/tag", json=wrong_data_to_add
    )
    assert response_add_tag.status_code == 404


async def test_edit_tag(db, auth_new_second_admin, new_tag):
    # 200 OK
    data_to_edit = {"title_tag": "Какой-то тег"}
    response_edit_tag = await auth_new_second_admin.put(
        url=f"admin/tag/{new_tag.id}", json=data_to_edit
    )
    assert response_edit_tag.status_code == 200
    tag_in_db = (await db.tags.get_filtered(id=new_tag.id))[0]
    assert tag_in_db.title_tag == data_to_edit.get("title_tag", None)

    # Пробуем изменить несуществующий тег
    response_edit_tag = await auth_new_second_admin.put(
        url="admin/tag/9999", json=data_to_edit
    )
    assert response_edit_tag.status_code == 404


async def test_add_reason(db, auth_new_second_admin):
    data_to_add = {"title": "Дезинформация"}

    # 200 OK
    response_add_reason = await auth_new_second_admin.post(
        "admin/reasons", json=data_to_add
    )
    json_response = response_add_reason.json()
    assert response_add_reason.status_code == 200
    assert await db.reasons.get_filtered(reason_id=json_response.get("reason_id"))

    # Пробуем добавить ту же причину
    response_add_reason = await auth_new_second_admin.post(
        "admin/reasons", json=data_to_add
    )
    assert response_add_reason.status_code == 409


async def test_edit_reason(db, auth_new_second_admin, new_reason):
    data_to_edit = {"title": "Нарушение правил площадки"}

    # 200 OK
    response_edit_reason = await auth_new_second_admin.put(
        url=f"admin/reasons/{new_reason.reason_id}", json=data_to_edit
    )
    response_json = response_edit_reason.json()
    db_reason = await db.reasons.get_one_or_none(reason_id=new_reason.reason_id)
    assert response_edit_reason.status_code == 200
    assert response_json is not None
    assert db_reason.title.lower() == data_to_edit.get("title", None).lower()

    # Пробуем изменить несуществующую причину
    response_edit_reason = await auth_new_second_admin.put(
        url="admin/reasons/9999", json=data_to_edit
    )
    assert response_edit_reason.status_code == 404


async def test_delete_reason(db, auth_new_second_admin, new_reason):
    # Пробуем удалить несуществующую причину
    response_delete_non_existent_reason = await auth_new_second_admin.delete(
        url="admin/reasons/9999"
    )
    assert response_delete_non_existent_reason.status_code == 404

    # 200 OK
    response_delete_non_existent_reason = await auth_new_second_admin.delete(
        url=f"admin/reasons/{new_reason.reason_id}"
    )
    assert response_delete_non_existent_reason.status_code == 200
    assert not await db.reasons.get_one_or_none(reason_id=new_reason.reason_id)


async def test_get_all_reports(db, auth_new_second_admin, new_report):
    response = await auth_new_second_admin.get(url="admin/reports")
    reports_in_db = await db.reports.get_all()
    assert response.status_code == 200
    assert len(response.json()) == len(reports_in_db)


async def test_mark_as_checked_report(db, auth_new_second_admin, new_report):
    response = await auth_new_second_admin.patch(url=f"admin/reports/{new_report.id}")
    assert response.status_code == 200
    # Проверяем, что пометилось как проверенное
    assert await db.reports.get_filtered(is_checked=True, id=new_report.id)


async def test_ban_user(
    db, auth_new_second_admin, new_admin, new_user, new_general_admin
):
    # 200 OK
    response_ban_user = await auth_new_second_admin.post(
        url=f"admin/ban/{new_user.user_id}",
        json={"comment": "оскарбления", "ban_until": "2035-07-15T09:46:57.309405Z"},
    )
    response_json = response_ban_user.json()
    assert response_ban_user.status_code == 200
    assert response_json
    assert await db.bans.get_one_or_none(ban_id=response_json.get("ban_id"))

    # Пытаемся забанить того же пользователя еще раз
    response_ban_already_banned_user = await auth_new_second_admin.post(
        url=f"admin/ban/{new_user.user_id}",
        json={"comment": "оскарбления", "ban_until": "2035-07-15T09:46:57.309405Z"},
    )
    assert response_ban_already_banned_user.status_code == 409

    # Пытаемся заблокировать несуществующего юзера
    response_ban_non_existent_user = await auth_new_second_admin.post(
        url="admin/ban/9999",
        json={"comment": "оскарбления", "ban_until": "2035-07-15T09:46:57.309405Z"},
    )
    assert response_ban_non_existent_user.status_code == 404

    # Пытаемся заблокировать админа
    response_ban_non_existent_user = await auth_new_second_admin.post(
        url=f"admin/ban/{new_admin.user_id}",
        json={"comment": "оскарбления", "ban_until": "2035-07-15T09:46:57.309405Z"},
    )
    assert response_ban_non_existent_user.status_code == 403

    # Пытаемся заблокировать главного админа
    response_ban_non_existent_user = await auth_new_second_admin.post(
        url=f"admin/ban/{new_general_admin.user_id}",
        json={"comment": "оскарбления", "ban_until": "2035-07-15T09:46:57.309405Z"},
    )
    assert response_ban_non_existent_user.status_code == 403


async def test_banned_user(auth_new_second_admin, new_user_with_ac, new_book):
    """Тестируем, что забаненный пользователь не сможет оставить отзыв"""
    user_client, user = new_user_with_ac
    # 200 OK
    response_ban_user = await auth_new_second_admin.post(
        url=f"admin/ban/{user.user_id}",
        json={"comment": "оскарбления", "ban_until": "2035-07-15T09:46:57.309405Z"},
    )
    assert response_ban_user.status_code == 200

    # Пробуем от имени забаненного пользователя публиковать отзыв
    response_add_review = await user_client.post(
        url=f"reviews/by_book/{new_book.book_id}",
        json={"rating": 1, "text": "Ха-ха! это ужасный спам!"},
    )
    assert response_add_review.status_code == 403


async def test_delete_ban(db, auth_new_second_admin, new_banned_user, new_book):
    response_unban_user = await auth_new_second_admin.delete(
        url=f"admin/ban/{new_banned_user.ban_id}"
    )
    assert response_unban_user.status_code == 200
    assert not await db.bans.get_one_or_none(ban_id=new_banned_user.ban_id)

    # Пробуем удалить несуществующий бан
    response_unban_user = await auth_new_second_admin.delete(url="admin/ban/9999")
    assert response_unban_user.status_code == 404


async def test_edit_ban(auth_new_second_admin, new_banned_user):
    data_to_edit = {"ban_until": "2040-07-15T09:46:57.309405Z"}

    # 200 OK
    response_edit_ban_date = await auth_new_second_admin.put(
        url=f"admin/ban/{new_banned_user.ban_id}", json=data_to_edit
    )
    assert response_edit_ban_date.status_code == 200

    # Пытаемся изменить несуществующий бан
    response_edit_non_existent_ban = await auth_new_second_admin.put(
        url="admin/ban/9999", json=data_to_edit
    )
    assert response_edit_non_existent_ban.status_code == 404


async def test_get_banned_users(db, auth_new_second_admin, new_banned_user):
    response_banned_users = await auth_new_second_admin.get(url="admin/banned_users")
    response_json = response_banned_users.json()
    banned_in_db = await db.bans.get_banned_users()
    assert response_banned_users.status_code == 200
    assert len(response_json) == len(banned_in_db)


async def test_generate_stmt(auth_new_second_admin):
    data_to_request = {"interval": "P3D"}
    response_generate_admin = await auth_new_second_admin.post(
        url="admin/statement", json=data_to_request
    )
    response_json = response_generate_admin.json()
    # Получаем абсолютный путь до файла-отчета
    stmt_path = Path(response_json.get("stmt_path", None))
    assert response_generate_admin.status_code == 200
    assert stmt_path.exists()
    stmt_path.unlink()


async def test_generate_auto_stmt(auth_new_second_admin):
    # Удаляем файл отчета, чтобы проверить обработку ошибок
    stmt_path = Path(f"{settings.STATEMENT_DIR_PATH}/users_statement_auto.xlsx")
    stmt_path.unlink()

    # Пытаемся получить еще не сгенерированный отчет
    response = await auth_new_second_admin.get(url="admin/statement/auto")
    assert response.status_code == 404

    # Генерируем автоматический отчет
    auto_statement.delay(test_mode=True)

    # Получаем уже сгенерированый отчет - 200 OK
    response = await auth_new_second_admin.get(url="admin/statement/auto")
    assert response.status_code == 200

    # Снова удаляем файл отчета, чтобы проверить обработку ошибок
    stmt_path = Path(f"{settings.STATEMENT_DIR_PATH}/users_statement_auto.xlsx")
    stmt_path.unlink()

    # Пытаемся получить отчет, файла которого нет
    response = await auth_new_second_admin.get(url="admin/statement/auto")
    assert response.status_code == 404

    # Создаем пустой файл отчета во избежание ошибок при следующих запусках
    with open(stmt_path, "wb"):
        pass

    # Пытаемся получить отчет пустого файла
    response = await auth_new_second_admin.get(url="admin/statement/auto")
    assert response.status_code == 404


async def test_get_stmts_by_date(auth_new_second_admin):
    now_as_str = date.today().strftime("%Y-%m-%d")

    # Пробуем получить отчеты, которых на эту дату нет
    response = await auth_new_second_admin.get(
        url=f"admin/statement?statement_date={now_as_str}"
    )
    assert response.status_code == 200

    # Генерируем отчет
    data_to_request = {"interval": "P3D"}
    response_generate_stmt = await auth_new_second_admin.post(
        url="admin/statement", json=data_to_request
    )
    response_json = response_generate_stmt.json()
    assert response_generate_stmt.status_code == 200

    # Получаем только что созданный отчет, на сегодняшнюю дату
    response = await auth_new_second_admin.get(
        url=f"admin/statement?statement_date={now_as_str}"
    )
    assert response.status_code == 200

    # Чистим созданные отчеты во избежание конфликтов
    stmt_path = Path(response_json.get("stmt_path", None))
    stmt_path.unlink()
