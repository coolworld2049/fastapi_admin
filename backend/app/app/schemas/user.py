import re
from difflib import SequenceMatcher
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, root_validator, validator

from app.models.classifiers import UserRole
from app.resources.reserved_username import usernames

password_exp = r"^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z].*[a-z]).{11,}$"
email_exp = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
username_exp = "[A-Za-z_0-9]*"


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = Field(...)
    username: str
    full_name: Optional[str]
    age: Optional[int]
    avatar: Optional[str]
    phone: Optional[str]
    is_active: bool = True
    is_superuser: bool = False

    @validator("username")
    def validate_username(cls, value):  # noqa
        assert value not in usernames, "This username is reserved"
        return value

    @root_validator()
    def validate_all(cls, values):  # noqa
        assert re.match(email_exp, values.get("email")), "Invalid email"
        assert re.match(
            username_exp, values.get("username")
        ), "Invalid characters in username"
        if values.get("username") and values.get("password") and values.get("email"):
            assert (
                SequenceMatcher(
                    None, values.get("username"), values.get("password")
                ).ratio()
                < 0.5
            ), "Password must not match username"
            try:
                assert (
                    SequenceMatcher(
                        None, values.get("password"), values.get("email").split("@")[0]
                    ).ratio()
                    < 0.4
                ), "Password must not match email"
            except AssertionError as e:
                print(e)
        return values

    @validator("phone")
    def validate_phone(cls, v):  # noqa
        regex = r"^(\+)[1-9][0-9\-\(\)\.]{9,15}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v

    class Config:
        use_enum_values = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

    @validator("password")
    def validate_password(cls, value):  # noqa
        assert re.match(password_exp, value), (
            "Make sure the password is: 11 characters long,"
            " 2 uppercase and 3 lowercase letters, 1 special char, 2 numbers"
        )
        return value


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
