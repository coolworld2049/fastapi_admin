import logging

from app.core.settings.app import AppSettings


class TestAppSettings(AppSettings):
    debug: bool = True
    title: str = "Test FastAPI example application"

    SECRET_KEY: str
    LOGGING_LEVEL: int = logging.DEBUG
