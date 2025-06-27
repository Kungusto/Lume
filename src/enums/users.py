from enum import Enum as pyEnum


class AllUsersRolesEnum(pyEnum):
    USER: str = "USER"
    AUTHOR: str = "AUTHOR"
    ADMIN: str = "ADMIN"

    def get_permission_level(role) -> int | None:
        levels = {
            "AllUsersRolesEnum.USER": 1,
            "AllUsersRolesEnum.AUTHOR": 2,
            "AllUsersRolesEnum.ADMIN": 3,
        }
        return levels.get(str(role), None)


class RegisterUserEnum(pyEnum):
    USER: str = "USER"
    AUTHOR: str = "AUTHOR"
