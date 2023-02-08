from __future__ import annotations

from app.core.celery_app import celery_app
from raven import Client

client_sentry = Client()
client_sentry.set_dsn()


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f'test task return {word}'
