import logging

from app.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True
    title: str = "Test FastAPI example application"

    JWT_SECRET_KEY: str
    LOGGING_LEVEL: int = logging.DEBUG
