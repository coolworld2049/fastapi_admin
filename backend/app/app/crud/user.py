from typing import Any, Optional, Sequence

from sqlalchemy import and_, select, Row, RowMapping
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas import RequestParams, UserCreate, UserUpdate
from app.services.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        create_data: dict = obj_in.dict()
        create_data.pop("password")
        db_obj = User(**create_data)  # noqa
        db_obj.hashed_password = get_password_hash(obj_in.password)
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            update_data.pop("password")
            # noinspection PyUnresolvedReferences
            update_data.update({"hashed_password": get_password_hash(obj_in.password)})
        result = await super().update(db, db_obj=db_obj, obj_in=update_data)
        return result

    # noinspection PyMethodMayBeStatic
    async def get_by_id(
        self, db: AsyncSession, *, id: int, role: str = None
    ) -> Optional[User]:
        q = select(User)
        if role:
            q = q.where(User.role == role)
        q = q.where(User.id == id)
        result: Result = await db.execute(q)
        return result.scalar()

    # noinspection PyMethodMayBeStatic
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        q = select(User).where(User.email == email)
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

    # noinspection PyMethodMayBeStatic,PyShadowingNames
    def is_online(self, user: User) -> bool:
        return user.is_online


user = CRUDUser(User)
