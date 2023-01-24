import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Tuple

from loguru import logger
from pydantic import PostgresDsn

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings


class AppSettings(BaseAppSettings):
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "fastapi_admin"
    version: str = "0.0.0"

    DEBUG: bool

    PG_PORT: int
    PG_NAME: str
    PG_SCHEMA: str
    PG_SUPERUSER: str
    PG_SUPERUSER_PASSWORD: str
    DATABASE_URL: PostgresDsn

    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    APP_NAME: str
    PG_TZ: str
    PG_VERSION: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    BOT_TOKEN: str

    log_file_max_bytes = 314572800

    max_connection_count: int = 10
    min_connection_count: int = 10

    api_prefix: str = '/api/v1'

    jwt_token_prefix: str = "token"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.DEBUG
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

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

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [
                InterceptHandler(level=self.logging_level),
                RotatingFileHandler('access.log', maxBytes=self.log_file_max_bytes, backupCount=1)
            ]

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])
