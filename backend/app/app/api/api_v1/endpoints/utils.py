from typing import Any

from app import models
from app import schemas
from app.api.dependencies import auth
from app.core.celery_app import celery_app
from fastapi import APIRouter
from fastapi import Depends
from pydantic.networks import EmailStr

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
async def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(auth.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
async def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(auth.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    ...
    return {"msg": "Test email sent"}
