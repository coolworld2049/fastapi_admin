from __future__ import annotations

from collections.abc import Callable

from app.core.settings.app import AppSettings
from fastapi import FastAPI
from loguru import logger


def create_start_app_handler(
    app: FastAPI,
    settings: AppSettings,
) -> Callable:
    async def start_app() -> None:
        pass

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    @logger.catch
    async def stop_app() -> None:
        pass

    return stop_app
