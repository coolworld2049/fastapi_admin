from __future__ import annotations

import pytest
from app import crud
from app.models import UserRole
from app.schemas.user import UserCreate
from app.schemas.user import UserUpdate
from app.services.security import verify_password
from app.tests.utils.utils import gen_random_password
from app.tests.utils.utils import random_email
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_create_user(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, role=UserRole.user.name)
    user = await crud.user.create(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, 'hashed_password')


@pytest.mark.asyncio
async def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, username=username)
    user = await crud.user.create(db, obj_in=user_in)
    authenticated_user = await crud.user.authenticate(
        db,
        email=email,
        password=password,
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


@pytest.mark.asyncio
async def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user = await crud.user.authenticate(db, email=email, password=password)
    assert user is None


@pytest.mark.asyncio
async def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, username=username)
    user = await crud.user.create(db, obj_in=user_in)
    is_active = await crud.user.is_active(user)
    assert is_active is True


@pytest.mark.asyncio
async def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, username=username)
    user = await crud.user.create(db, obj_in=user_in)
    is_active = await crud.user.is_active(user)
    assert is_active


@pytest.mark.asyncio
async def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = await crud.user.create(db, obj_in=user_in)
    is_superuser = await crud.user.is_superuser(user)
    assert is_superuser is True


@pytest.mark.asyncio
async def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, username=username)
    user = await crud.user.create(db, obj_in=user_in)
    is_superuser = await crud.user.is_superuser(user)
    assert is_superuser is False


@pytest.mark.asyncio
async def test_get_user(db: Session) -> None:
    password = gen_random_password()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = await crud.user.create(db, obj_in=user_in)
    user_2 = await crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


@pytest.mark.asyncio
async def test_update_user(db: Session) -> None:
    password = gen_random_password()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = await crud.user.create(db, obj_in=user_in)
    new_password = gen_random_password()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    await crud.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = await crud.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
