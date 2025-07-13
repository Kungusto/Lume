"""
Запустить этот файл отдельно:
pytest -s -v tests/integration/admin/test_api.py
"""


import random

import pytest


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



