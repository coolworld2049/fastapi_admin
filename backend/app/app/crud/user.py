from collections.abc import Sequence
from typing import Any
from typing import Optional

from loguru import logger
from sqlalchemy import Row
from sqlalchemy import RowMapping
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.core.config import get_app_settings
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas import RequestParams
from app.schemas import UserCreate
from app.schemas import UserUpdate
from app.services.security import get_password_hash
from app.services.security import verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    @staticmethod
    async def password_to_hash(_data: UserCreate | UserUpdate):
        data = _data.dict()
        if data.get("password"):
            hashed_password = get_password_hash(data.get("password"))
            data.update({"hashed_password": hashed_password})
            data.pop("password")
            data.pop("password_confirm")
        return User(**data) # noqa

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = await self.password_to_hash(obj_in)
        try:
            db.add(db_obj)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(e.__dict__['orig']) if get_app_settings().APP_ENV == 'dev' else None
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any],
    ) -> User:
        db_obj = await self.password_to_hash(obj_in)
        result = await super().update(db, db_obj=db_obj, obj_in=db_obj)
        return result

    # noinspection PyMethodMayBeStatic
    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        id: int,
        role: str = None,
    ) -> Optional[User]:
        q: Select = select(User)
        if role:
            q = q.where(User.role == role)
        q = q.where(User.id == id)
        result: Result = await db.execute(q)
        return result.scalar()

    # noinspection PyMethodMayBeStatic
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        q: Select = select(User).where(User.email == email)
        result: Result = await db.execute(q)
        return result.scalar()

    async def constr_user_role_filter(self, roles: list[str], column: Any = None):
        c_filter = None
        if roles:
            if column is None:
                c_filter = and_(self.model.role.in_(tuple(roles)))
            else:
                c_filter = and_(column.in_(tuple(roles)))
        return c_filter

    async def get_multi_with_role(
        self,
        db: AsyncSession,
        request_params: RequestParams,
        roles: list[str] = None,
    ) -> tuple[Sequence[Row | RowMapping | Any], Any]:
        flt = await self.constr_user_role_filter(roles)
        users, total = await super().get_multi(db, request_params, flt)
        return users, total

    # noinspection PyShadowingNames
    async def authenticate(
        self,
        *,
        email: str,
        password: str,
        db: AsyncSession,
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    # noinspection PyMethodMayBeStatic,PyShadowingNames
    def is_active(self, user: User) -> bool:
        return user.is_active

    # noinspection PyMethodMayBeStatic,PyShadowingNames
    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
