import pathlib

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.api_v1.api import api_router
from app.api.api_v1.errors.http_error import http_error_handler
from app.api.api_v1.errors.validation_error import http422_error_handler
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    settings = get_app_settings()

    get_app_settings().configure_logging()

    application = FastAPI(**get_app_settings().fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_app_settings().allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        expose_headers=["Content-Range", "Range"],
        allow_headers=["*", "Authorization", "Range", "Content-Range"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=get_app_settings().api_prefix)

    application.mount("/static", StaticFiles(directory=f"{pathlib.Path().cwd()}/static", html=True),
                      name="static")

    return application


app = get_application()
