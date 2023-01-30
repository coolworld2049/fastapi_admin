from datetime import timedelta
from typing import Any

from app import crud, models, schemas
from app.api.dependencies import auth, database
from app.core.config import get_app_settings
from app.services import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(database.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = await crud.user.authenticate(
            email=form_data.username, password=form_data.password, db=db
        )
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Incorrect email or password",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )
    exp = timedelta(minutes=get_app_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.create_access_token(
        sub=user.id, expires_delta=exp, scopes=form_data.scopes
    )
    return token


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(auth.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user
