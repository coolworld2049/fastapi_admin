import random
import string
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import get_app_settings
from app.models import UserRole
from app.schemas.user import UserCreate
from app.tests.test_data import fake
from app.tests.utils.utils import random_email, gen_random_password


async def creat_test_user(role: UserRole, username: str):
    user_in = schemas.UserCreate(
        email=f"{role}{username}@gmail.com",
        password=gen_random_password(),
        username=f"{role}{username}{random.randint(1000, 10000)}",
        full_name=fake.name(),
        age=random.randint(18, 25),
        phone="+7" + "".join(random.choice(string.digits) for _ in range(10)),
        role=role,
    )
    return await crud.user.create(db, obj_in=user_in)


@pytest.mark.asyncio
async def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.get(
        f"{get_app_settings().api_v1}/users/me", headers=superuser_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["email"] == get_app_settings().FIRST_SUPERUSER_EMAIL


@pytest.mark.asyncio
async def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    r = client.get(
        f"{get_app_settings().api_v1}/users/me", headers=normal_user_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["email"] == get_app_settings().FIRST_SUPERUSER_EMAIL


@pytest.mark.asyncio
async def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    email = random_email()
    password = gen_random_password()
    data = {"email": email, "password": password}
    r = client.post(
        f"{get_app_settings().api_v1}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = await crud.user.get_by_email(db, email=email)
    assert user
    assert user.email == created_user["email"]


@pytest.mark.asyncio
async def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db, obj_in=user_in)
    user_id = user.id
    r = client.get(
        f"{get_app_settings().api_v1}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = await crud.user.get_by_email(db, email=email)
    assert existing_user
    assert existing_user.email == api_user["email"]


@pytest.mark.asyncio
async def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    email = random_email()
    # username = email
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password)
    crud.user.create(db, obj_in=user_in)
    data = {"email": email, "password": password}
    r = client.post(
        f"{get_app_settings().api_v1}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


@pytest.mark.asyncio
async def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    email = random_email()
    password = gen_random_password()
    data = {"email": email, "password": password}
    r = client.post(
        f"{get_app_settings().api_v1}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(email=email, password=password, role=UserRole.anon)
    await crud.user.create(db, obj_in=user_in)

    email2 = random_email()
    password2 = gen_random_password()
    user_in2 = UserCreate(email=email2, password=password2, role=UserRole.anon)
    await crud.user.create(db, obj_in=user_in2)

    r = client.get(
        f"{get_app_settings().api_v1}/users/", headers=superuser_token_headers
    )
    all_users = r.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item
