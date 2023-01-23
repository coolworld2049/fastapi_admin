from datetime import datetime

import pytz
from sqlalchemy import CheckConstraint, Column, BigInteger, Text, text, SmallInteger, String, Boolean, DateTime

from app.core.config import get_app_settings
from app.db import user_role
from app.models.domain.base import BaseDbModel


class User(BaseDbModel):
    __tablename__ = 'user'
    __table_args__ = (
        CheckConstraint('full_name <> (role)::text'),
        CheckConstraint('username <> (role)::text'),
    )

    id = Column(BigInteger, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    hashed_password = Column(Text)
    role = Column(user_role, nullable=False,
                  server_default=text("'anon'::user_role"))
    full_name = Column(Text)
    username = Column(Text, nullable=False, unique=True)
    age = Column(SmallInteger)
    phone = Column(String(20))
    avatar = Column(Text)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_superuser = Column(Boolean, nullable=False, server_default=text("false"))
    created_at = Column(
        DateTime(timezone=True), server_default=text("LOCALTIMESTAMP"),
        default=datetime.now(tz=pytz.timezone(get_app_settings().PG_TZ))
    )
    updated_at = Column(DateTime(timezone=True), server_default=None)
