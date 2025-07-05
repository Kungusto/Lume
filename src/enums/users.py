from enum import Enum as pyEnum


class AllUsersRolesEnum(str, pyEnum):
    USER: str = "USER"
    AUTHOR: str = "AUTHOR"
    ADMIN: str = "ADMIN"
    GENERAL_ADMIN: str = "GENERAL_ADMIN"

    def get_permission_level(role) -> int | None:
        levels = {
            "USER": 1,
            "AUTHOR": 2,
            "ADMIN": 3,
            "GENERAL_ADMIN": 4,
        }
        return levels.get(str(role), None)


class RegisterUserEnum(str, pyEnum):
    USER: str = "USER"
    AUTHOR: str = "AUTHOR"
