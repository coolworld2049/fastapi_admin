from pathlib import Path

from app.api.api_v1.api import api_router
from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.api.openapi import custom_openapi, use_route_names_as_operation_ids
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

current_file = Path(__file__)
current_file_dir = current_file.parent
project_root = current_file_dir.parent
project_root_absolute = project_root.resolve()
project_static_path = project_root_absolute / "app/static"


def get_application() -> FastAPI:
    settings = get_app_settings()

    get_app_settings().configure_logging()

    application = FastAPI(**get_app_settings().fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=get_app_settings().BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        expose_headers=["Content-Range", "Range"],
        allow_headers=["*", "Authorization", "Range", "Content-Type", "Content-Range"],
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

    application.include_router(api_router, prefix=get_app_settings().api_v1)

    custom_openapi(application)
    use_route_names_as_operation_ids(application)

    application.mount(
        "/static", StaticFiles(directory=project_static_path), name="static"
    )

    return application


app = get_application()


@app.get("/")
async def root(request: Request):
    return FileResponse(path=project_static_path / "html/index.html")
