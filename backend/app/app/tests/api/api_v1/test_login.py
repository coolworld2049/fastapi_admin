from __future__ import annotations

from typing import Dict

import pytest
from app.core.config import get_app_settings
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_get_access_token(client: TestClient) -> None:
    login_data = {
        'username': get_app_settings().FIRST_SUPERUSER_EMAIL,
        'password': get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f'{get_app_settings().api_v1}/login/access-token', data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert 'access_token' in tokens
    assert tokens['access_token']


@pytest.mark.asyncio
async def test_use_access_token(
    client: TestClient, superuser_token_headers: Dict[str, str],
) -> None:
    r = client.post(
        f'{get_app_settings().api_v1}/login/test-token',
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert 'email' in result
