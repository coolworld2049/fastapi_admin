from __future__ import annotations

import asyncio
from collections.abc import Generator
from typing import Dict

import pytest
from app.core.config import get_app_settings
from app.db.session import SessionLocal
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture(scope='session')
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope='module')
def client() -> Generator:
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='module')
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope='module')
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return asyncio.run(
        authentication_token_from_email(
            client=client, email=get_app_settings().FIRST_SUPERUSER_EMAIL, db=db,
        ),
    )
