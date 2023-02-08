from __future__ import annotations

from app.db.session import Base
from app.models.mixins import TimestampsMixin
from app.models.user.role import UserRole
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM


class User(Base, TimestampsMixin):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint('full_name <> (role)::text'),
        CheckConstraint('username <> (role)::text'),
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
    is_active = Column(Boolean, nullable=False, server_default=text('true'))
    is_superuser = Column(Boolean, nullable=False, server_default=text('false'))
