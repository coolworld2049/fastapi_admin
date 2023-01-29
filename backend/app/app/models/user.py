from sqlalchemy import (Boolean, CheckConstraint, Column, SmallInteger, String,
                        Text, text)
from sqlalchemy.dialects.postgresql import ENUM

from app.models import TimestampsMixin
from app.models.base import BaseDbModel
from app.models.classifiers import UserRole


class User(BaseDbModel, TimestampsMixin):
    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint("full_name <> (role)::text"),
        CheckConstraint("username <> (role)::text"),
    )
    email = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text)
    role = Column(
        ENUM(*UserRole.to_list(), name=UserRole.snake_case_name()),
        nullable=False,
        server_default=text("'anon'::user_role"),
    )
    full_name = Column(Text)
    username = Column(Text, nullable=False, unique=True)
    age = Column(SmallInteger)
    phone = Column(String(20))
    avatar = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("false"))
