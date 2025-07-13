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
