from __future__ import annotations

from typing import Dict

from app import crud
from app.core.config import get_app_settings
from app.models.user.user import User
from app.schemas.user import UserCreate
from app.schemas.user import UserUpdate
from app.tests.utils.utils import gen_random_password
from app.tests.utils.utils import random_email
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def user_authentication_headers(
    *,
    client: TestClient,
    email: str,
    password: str,
) -> Dict[str, str]:
    data = {'username': email, 'password': password}

    r = client.post(f'{get_app_settings().api_v1}/login/access-token', data=data)
    response = r.json()
    auth_token = response['access_token']
    headers = {'Authorization': f'Bearer {auth_token}'}
    return headers


async def create_random_user(db: Session) -> User:
    email = random_email()
    password = gen_random_password()
    user_in = UserCreate(username=email, email=email, password=password)
    user = await crud.user.create(db=db, obj_in=user_in)
    return user


async def authentication_token_from_email(
    *,
    client: TestClient,
    email: str,
    db: Session,
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = gen_random_password()
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(username=email, email=email, password=password)
        user = await crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = await crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
