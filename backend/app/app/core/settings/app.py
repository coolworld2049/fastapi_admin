import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Tuple

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings
from loguru import logger


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    api_v1: str = "/api/v1"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "fastapi_admin"
    version: str = "0.0.0"

    APP_NAME: str
    TZ: str
    DEBUG: bool

    DOMAIN: str
    PORT: int

    BACKEND_CORS_ORIGINS: List[str]
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    PG_HOST: str
    PG_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_HTTP_PORT: int
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    BOT_TOKEN: str

    LOGGING_LEVEL: str = "INFO"
    LOGGERS: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")
    LOG_FILE_MAX_BYTES = 314572800

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.DEBUG,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    @property
    def get_postgres_dsn(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.POSTGRES_DB}"

    @property
    def get_rabbitmq_dsn(self):
        return f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.LOGGERS:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [
                InterceptHandler(level=self.LOGGING_LEVEL),
                RotatingFileHandler(
                    "access.log", maxBytes=self.LOG_FILE_MAX_BYTES, backupCount=1
                ),
            ]

        logger.configure(handlers=[{"sink": sys.stdout, "level": self.LOGGING_LEVEL}])
