import os

from celery import Celery

celery_app = Celery("worker", broker=os.getenv("AMQP_DSN"))

celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
