from celery import Celery

from app.core.config import get_app_settings

celery_app = Celery("worker", broker=get_app_settings().get_rabbitmq_dsn)

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
