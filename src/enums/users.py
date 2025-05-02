from enum import Enum as pyEnum

class RolesUsersEnum(pyEnum) :
    USER = "USER"
    AUTHOR = "AUTHOR"

class AllUsersRolesEnum(pyEnum) :
    USER = "USER"
    AUTHOR = "AUTHOR"
    ADMIN = "ADMIN"

class OnlyAdmin(pyEnum) :
    ADMIN = "ADMIN"
