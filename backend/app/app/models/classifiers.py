from app.models.mixins import EnumMixin


class UserRole(str, EnumMixin):
    admin = "admin"
    manager = "manager"
    anon = "anon"
