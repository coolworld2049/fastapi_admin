import re
from difflib import SequenceMatcher
from typing import Optional

from loguru import logger
from pydantic import EmailStr, Field, validator, root_validator, BaseModel

from app.models import UserRole
from app.resources.reserved_username import reserved_usernames_list


password_exp = r"^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z].*[a-z]).{11,}$"
email_exp = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
username_exp = "[A-Za-z_0-9]*"


class UserValidator:
    @staticmethod
    def values_match_ratio(a, b, match_value: float):
        return SequenceMatcher(None, a, b).ratio() < match_value

    @classmethod
    def check_valid_username(cls, values):
        assert re.match(email_exp, values.get("email")), "Invalid email"
        assert re.match(
            username_exp,
            values.get("username"),
        ), "Invalid characters in username"

    @classmethod
    def check_password_strongness(cls, values):
        try:
            assert cls.values_match_ratio(
                values.get("username"), values.get("password"), 0.6
            ), "Password must not match username"
            assert cls.values_match_ratio(
                values.get("password"), values.get("email").split("@")[0], 0.4
            ), "Password must not match email"
        except AssertionError as e:
            logger.error(e.args)

    @root_validator()
    def validate_all(cls, values):
        try:
            assert values.get("email")
            assert values.get("role")
            assert values.get("username")
        except AssertionError as e:
            logger.error(e.args)

        cls.check_valid_username(values)

        if values.get("username") and values.get("password") and values.get("email"):
            cls.check_password_strongness(values)
        return values

    @validator("username")
    def validate_username(cls, value):  # noqa
        assert value not in reserved_usernames_list, "This username is reserved"
        return value

    @validator("password")
    def validate_password(cls, value):  # noqa
        assert re.match(password_exp, value), (
            "Make sure the password is: 11 characters long,"
            " 2 uppercase and 3 lowercase letters, 1 special char, 2 numbers"
        )
        return value

    @validator("phone")
    def validate_phone(cls, v):  # noqa
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v


class UserBase(BaseModel, UserValidator):
    email: EmailStr
    role: UserRole = Field(UserRole.user.name)
    username: str
    full_name: Optional[str]
    age: Optional[int] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        use_enum_values = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    password_confirm: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config(UserBase.Config):
        orm_mode = True


# Additional properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
    hashed_password: str


# Additional properties to return via API
class User(UserInDBBase):
    class Config:
        fields = {
            "is_superuser": {"exclude": True},
            "hashed_password": {"exclude": True},
        }
