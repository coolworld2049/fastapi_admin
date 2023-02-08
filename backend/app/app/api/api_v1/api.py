from __future__ import annotations

from app.api.api_v1.endpoints import login
from app.api.api_v1.endpoints import users
from app.api.api_v1.endpoints import utils
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(login.router, tags=['login'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(utils.router, prefix='/utils', tags=['utils'])
