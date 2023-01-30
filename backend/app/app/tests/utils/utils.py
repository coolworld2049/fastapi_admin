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
    r = client.post(f"{get_app_settings().api_v1}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def gen_random_password(number: int = random.randint(10, 100), rnd_str_length: int = 4):
    r_str = "".join(
        random.choice(string.ascii_letters) for _ in range(rnd_str_length)
    ).capitalize()
    return (
        f"{''.join(random.choice(string.ascii_letters) for _ in range(rnd_str_length)).capitalize()}"
        f"{r_str}{number}{number * 2}"
        f"{''.join(random.choice(string.ascii_letters) for _ in range(rnd_str_length)).capitalize()}"
        f"{random.choice(['!', '@', '#', '$', '&', '*'])}"
    )
