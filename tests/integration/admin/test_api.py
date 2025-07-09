"""
Запустить этот файл отдельно: 
pytest -s -v tests/integration/admin/test_api.py
"""

async def test_change_user_role(auth_ac_admin, seed_users):
    # изменить роль несуществующему пользователю
    response_change_role_non_existent_user = await auth_ac_admin.patch(
        url="admin/9999/change_role", json={"role": "AUTHOR"}
    )
    assert response_change_role_non_existent_user.status_code == 404

    # изменить роль главного админа на обычного пользователя
    # *id главного админа = 7
    response_change_role_to_general_admin = await auth_ac_admin.patch(
        url="admin/7/change_role", json={"role": "USER"}
    )
    assert response_change_role_to_general_admin.status_code == 403

    # изменить роль пользователя на админа
    response_change_role = await auth_ac_admin.patch(
        url="admin/8/change_role", json={"role": "ADMIN"}
    )
    assert response_change_role.status_code == 200

    # изменить роль пользователя, ставшего админом
    response_change_role = await auth_ac_admin.patch(
        url="admin/8/change_role", json={"role": "USER"}
    )
    assert response_change_role.status_code == 403
