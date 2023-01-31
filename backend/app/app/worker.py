from raven import Client

from app.core.celery_app import celery_app

client_sentry = Client()
client_sentry.set_dsn()


@celery_app.task
def add(x, y):
    return x + y


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"
