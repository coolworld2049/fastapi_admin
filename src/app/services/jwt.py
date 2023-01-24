from datetime import datetime, timedelta
from typing import Union, Any, List

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app import schemas
from app.core.config import get_app_settings

cryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2Scheme = OAuth2PasswordBearer(tokenUrl=f"{get_app_settings().api_prefix}/login/access-token")


def create_access_token(
        sub: Union[int, Any],
        scopes: List[str] = None,
        expires_delta: timedelta = None,
) -> dict:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=get_app_settings().ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"expires_delta": str(expire), "sub": str(sub), "scopes": scopes}
    encoded_jwt = jwt.encode(to_encode, get_app_settings().SECRET_KEY, algorithm=get_app_settings().ALGORITHM)

    token = schemas.Token(access_token=encoded_jwt, token_type="bearer", **to_encode)
    return token.dict()
