from typing import Dict

from app.core.config import get_app_settings
from fastapi.testclient import TestClient


def test_celery_worker_test(
    client: TestClient,
    superuser_token_headers: Dict[str, str],
) -> None:
    data = {"msg": "tests"}
    r = client.post(
        f"{get_app_settings().api_v1}/utils/tests-celery/",
        json=data,
        headers=superuser_token_headers,
    )
    response = r.json()
    assert response["msg"] == "Word received"
