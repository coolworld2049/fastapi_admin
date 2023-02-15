from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM

from app.models import UserRole
from app.models.base import BaseModel
from app.models.mixins import TimestampsMixin


class User(BaseModel, TimestampsMixin):
    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint("full_name <> (role)::text", 'full_name != role'),
        CheckConstraint("username <> (role)::text", 'username != role'),
    )
    id = Column(BigInteger, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text)
    role = Column(
        ENUM(*UserRole.to_list(), name=UserRole.snake_case_name()),
        nullable=False,
        server_default=text(f"'{UserRole.user.name}'::user_role"),
    )
    full_name = Column(Text)
    username = Column(Text, nullable=False, unique=True)
    age = Column(SmallInteger)
    phone = Column(String(20))
    avatar = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("false"))
