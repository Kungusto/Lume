from enum import Enum as pyEnum


class AllUsersRolesEnum(pyEnum):
    USER: str = "USER"
    AUTHOR: str = "AUTHOR"
    ADMIN: str = "ADMIN"

    def get_permission_level(role) -> int | None:
        levels = {
            "USER": 1,
            "AUTHOR": 2,
            "ADMIN": 3,
        }
        return levels.get(str(role), None)


class RegisterUserEnum(pyEnum):
    USER: str = "USER"
    AUTHOR: str = "AUTHOR"
