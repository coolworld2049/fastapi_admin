from __future__ import annotations

from app.models.mixins import EnumMixin


class UserRole(str, EnumMixin):
    admin = 'admin'
    user = 'user'
