import re
from difflib import SequenceMatcher
from typing import Optional

from loguru import logger
from pydantic import EmailStr, validator, root_validator, BaseModel, PrivateAttr

from app.models import UserRole
from app.resources.reserved_username import reserved_usernames_list

password_exp = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
password_conditions = """
Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character
"""
username_exp = "[A-Za-z_0-9]*"


class UserBase(BaseModel):
    email: Optional[EmailStr]
    role: UserRole = UserRole.user.name
    username: Optional[str]
    full_name: Optional[str]
    age: Optional[int]
    avatar: Optional[str]
    phone: Optional[str]
    _is_active: bool = True
    _is_superuser: bool = False

    class Config:
        use_enum_values = True

    @validator("username")
    def validate_username(cls, value):  # noqa
        assert re.match(
            username_exp,
            value,
        ), "Invalid characters in username"
        assert value not in reserved_usernames_list, "This username is reserved"
        return value

    @validator("phone")
    def validate_phone(cls, v):  # noqa
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str
    password_confirm: str

    @classmethod
    def check_password_strongness(cls, values):
        def values_match_ratio(a, b):
            return SequenceMatcher(None, a, b).ratio() if a and b else None

        assert values.get("email"), 'email is None'
        assert values.get("username"), 'username is None'
        assert values.get("password"), 'password is None'

        username_password_match: float = values_match_ratio(
            values.get("username"),
            values.get("password"),
        )
        assert username_password_match < 0.5, "Password must not match username"

        email_password_match: float = values_match_ratio(
            values.get("email").split("@")[0],
            values.get("password"),
        )
        assert email_password_match < 0.5, "Password must not match email"
        return values

    @root_validator(pre=True)
    def validate_all(cls, values):
        if values.get("password_confirm"):
            assert values.get("password") == values.get("password_confirm"), 'Passwords mismatch.'
        if values.get("id") is None:
            try:
                return cls.check_password_strongness(values)
            except AssertionError as e:
                logger.error(e.args)

    @validator("password")
    def validate_password(cls, value):  # noqa
        assert re.match(password_exp, value, flags=re.M), password_conditions
        return value


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
    _hashed_password: str
