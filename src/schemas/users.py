from datetime import date, datetime
from pydantic import BaseModel, EmailStr, field_validator, constr
from src.enums.users import AllUsersRolesEnum, RegisterUserEnum
from src.exceptions.auth import (
    TooShortPasswordHTTPException,
    TooLongPasswordHTTPException,
)


class User(BaseModel):
    user_id: int
    role: AllUsersRolesEnum
    email: EmailStr
    name: str
    surname: str
    nickname: str
    last_activity: date
    registation_date: date


class UserWithBanDate(User):
    ban_until: datetime | None


class UserWithHashedPassword(User):
    hashed_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegistrate(BaseModel):
    role: RegisterUserEnum
    email: EmailStr
    name: constr(min_length=2)  # type: ignore
    surname: constr(min_length=2)  # type: ignore
    nickname: constr(min_length=5)  # type: ignore
    password: str

    @field_validator("password")
    @classmethod
    def check_password_len(cls, value: str):
        if len(value) < 5:
            raise TooShortPasswordHTTPException
        elif len(value) > 50:
            raise TooLongPasswordHTTPException
        return value


class UserAdd(BaseModel):
    role: AllUsersRolesEnum
    email: EmailStr
    name: str
    surname: str
    nickname: str
    hashed_password: str


class UserPUT(BaseModel):
    email: EmailStr
    name: str
    surname: str
    nickname: str


class UserPATCH(BaseModel):
    email: EmailStr | None
    name: str | None
    surname: str | None
    nickname: str | None
    hashed_password: str | None


class UserPublicData(BaseModel):
    name: str
    surname: str
    nickname: str


class UserRolePUT(BaseModel):
    role: AllUsersRolesEnum


