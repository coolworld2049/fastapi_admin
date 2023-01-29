import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import get_app_settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": get_app_settings().FIRST_SUPERUSER_EMAIL,
        "password": get_app_settings().FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{get_app_settings().API_V1}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
