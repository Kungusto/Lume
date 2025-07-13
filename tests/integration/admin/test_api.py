"""
Запустить этот файл отдельно:
pytest -s -v tests/integration/admin/test_api.py
"""

async def test_change_user_role(auth_new_admin, new_user, new_general_admin):
    # изменить роль несуществующему пользователю
    response_change_role_non_existent_user = await auth_new_admin.patch(
        url="admin/9999/change_role", json={"role": "AUTHOR"}
    )
    assert response_change_role_non_existent_user.status_code == 404

    # изменить роль главного админа на обычного пользователя
    response_change_role_to_general_admin = await auth_new_admin.patch(
        url=f"admin/{new_general_admin.user_id}/change_role", json={"role": "USER"}
    )
    assert response_change_role_to_general_admin.status_code == 403

    # изменить роль пользователя на админа
    response_change_role = await auth_new_admin.patch(
        url=f"admin/{new_user.user_id}/change_role", json={"role": "ADMIN"}
    )
    assert response_change_role.status_code == 200

    # изменить роль пользователя, ставшего админом
    response_change_role = await auth_new_admin.patch(
        url=f"admin/{new_user.user_id}/change_role", json={"role": "USER"}
    )
    assert response_change_role.status_code == 403


async def test_add_already_exist_genre(auth_new_admin, new_genre): 
    response_add_already_exist_genre = await auth_new_admin.post(
        "/admin/genres", json={"title": new_genre.title}
    )
    assert response_add_already_exist_genre.status_code == 409


async def test_add_genre(auth_new_admin):
    response_add_genre = await auth_new_admin.post(
        "/admin/genres", json={"title": "Страшилки!"}
    )
    assert response_add_genre.status_code == 200


async def test_edit_genre(db, auth_new_admin, new_genre): 
    update_data = {"title": "Роман_"}
    response_edit_genre = await auth_new_admin.put(
        f"/admin/genres/{new_genre.genre_id}", json=update_data
    )
    assert response_edit_genre.status_code == 200
    db_genre = await db.genres.get_one(genre_id=new_genre.genre_id)
    assert db_genre.title == update_data.get("title", None)

    response_edit_genre = await auth_new_admin.put(
        "/admin/genres/9999", json={"title": "Изменяю несуществующий жанр!"}
    )
    assert response_edit_genre.status_code == 404


async def test_delete_genre(db, auth_new_admin, new_genre): 
    # 200 OK
    response_delete_genre = await auth_new_admin.delete(
        f"/admin/genres/{new_genre.genre_id}"
    )
    assert response_delete_genre.status_code == 200
    assert not await db.genres.get_filtered(genre_id=new_genre.genre_id)

    # Пробуем удалить несуществующий жанр
    response_delete_genre = await auth_new_admin.delete(
        f"/admin/genres/9999"
    )
    assert response_delete_genre.status_code == 404


async def test_delete_tag(db, auth_new_admin, new_tag):
    # 200 OK
    response_delete_tag = await auth_new_admin.delete(
        url=f"admin/tag/{new_tag.id}"
    )
    assert response_delete_tag.status_code == 200
    assert not await db.tags.get_filtered(id=new_tag.id)

    # Пробуем удалить несуществующий тег
    response_delete_non_existent_tag = await auth_new_admin.delete(
        url=f"admin/tag/9999"
    )
    assert response_delete_non_existent_tag.status_code == 404


async def test_add_tag(db, auth_new_admin, new_book): 
    # 200 OK 
    data_to_add = {"book_id": new_book.book_id, "title_tag": "Много роз!"}
    response_add_tag = await auth_new_admin.post(
        url="admin/tag", json=data_to_add
    )
    assert response_add_tag.status_code == 200
    assert await db.tags.get_filtered(book_id=new_book.book_id, title_tag=data_to_add.get("title_tag", None))

    # Пробуем тот же самый тег, к той же самой книге
    response_add_tag = await auth_new_admin.post(
        url="admin/tag", json=data_to_add
    )
    assert response_add_tag.status_code == 409

    # Пробуем добавить тег к несуществующей книге
    wrong_data_to_add = {"book_id": 9999, "title_tag": "Много роз!"}
    response_add_tag = await auth_new_admin.post(
        url="admin/tag", json=wrong_data_to_add
    )
    assert response_add_tag.status_code == 404


async def test_edit_tag(db, auth_new_admin, new_tag):
    # 200 OK 
    data_to_edit = {"title_tag": "Какой-то тег"}
    response_edit_tag = await auth_new_admin.put(
        url=f"admin/tag/{new_tag.id}", json=data_to_edit
    )
    assert response_edit_tag.status_code == 200
    tag_in_db = (await db.tags.get_filtered(id=new_tag.id))[0]
    assert tag_in_db.title_tag == data_to_edit.get("title_tag", None)

    # Пробуем изменить несуществующий тег
    response_edit_tag = await auth_new_admin.put(
        url=f"admin/tag/9999", json=data_to_edit
    )
    assert response_edit_tag.status_code == 404
