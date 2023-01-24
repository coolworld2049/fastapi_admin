from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession


from app import crud, schemas, models
from app.api.api_v1.dependencies import database, authentication, params
from app.models.classifiers import UserRole
from app.models.user import User

router = APIRouter()


# noinspection PyUnusedLocal
@router.get("/", response_model=List[schemas.User])
async def read_users(
        response: Response,
        db: AsyncSession = Depends(database.get_session),
        current_user: models.User = Depends(authentication.get_current_active_user),
        request_params: schemas.RequestParams = Depends(params.parse_react_admin_params(User))
) -> Any:
    """
    Retrieve users.
    """
    users, total = await crud.user.get_multi(db, request_params)
    response.headers["Content-Range"] = f"{request_params.skip}-{request_params.skip + len(users)}/{total}"
    return users


# noinspection PyUnusedLocal
@router.post("/", response_model=schemas.User)
async def create_user(
        *,
        db: AsyncSession = Depends(database.get_session),
        user_in: schemas.UserCreate,
        current_user: models.User = Depends(authentication.get_current_active_user),
) -> Any:
    """
    Create new user.
    """

    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="privelegies error",
        )
    new_user = await crud.user.create(db, obj_in=user_in)
    return new_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
        *,
        db: AsyncSession = Depends(database.get_session),
        password: str = Body(None),
        email: EmailStr = Body(None),
        current_user: models.User = Depends(authentication.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password:
        user_in.password = password
    if email:
        user_in.email = email
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


# noinspection PyUnusedLocal
@router.get("/me", response_model=schemas.User)
async def read_user_me(
        response: Response,
        db: AsyncSession = Depends(database.get_session),
        current_user: models.User = Depends(authentication.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    user = await crud.user.get(db, current_user.id)
    response.headers["Content-Range"] = f"{0}-{1}/{1}"
    return user


# noinspection PyUnusedLocal
@router.get("/{id}", response_model=schemas.User)
async def read_user_by_id(
        id: int,
        current_user: models.User = Depends(authentication.get_current_active_user),
        db: AsyncSession = Depends(database.get_session),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(db, id)
    return user


# noinspection PyUnusedLocal
@router.put("/{id}", response_model=schemas.User)
async def update_user(
        *,
        db: AsyncSession = Depends(database.get_session),
        id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(authentication.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


# noinspection PyUnusedLocal
@router.delete("/{id}", response_model=schemas.User)
async def delete_user(
        *,
        id: int,
        db: AsyncSession = Depends(database.get_session),
        current_user: models.User = Depends(authentication.get_current_active_user),
) -> Any:
    """
    Delete an task.
    """
    item = await crud.user.get(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.is_active:
        raise HTTPException(status_code=404, detail="Acive user cannot be removed")
    if item.is_superuser:
        raise HTTPException(status_code=404, detail="Superuser cannot be removed")

    item = await crud.user.remove(db=db, id=id)
    return item


# ----------------------------------------------------------------------------------------------------------------------


# noinspection PyUnusedLocal
@router.get("/role/{rolname}", response_model=List[schemas.User])
async def read_users_by_role_id(
        response: Response,
        db: AsyncSession = Depends(database.get_session),
        current_user: models.User = Depends(authentication.get_current_active_user),
        request_params: schemas.RequestParams = Depends(params.parse_react_admin_params(User)),
        rolname: str = Query(None),
) -> Any:
    """
    Retrieve users.
    """
    roles = None

    if rolname in UserRole.to_list():
        roles = [rolname]
    elif not roles:
        raise HTTPException(404, 'role not set')
    user, total = await crud.user.get_multi_with_role(db, request_params, roles)
    response.headers["Content-Range"] = f"{request_params.skip}-{request_params.skip + len(user)}/{total}"
    return user


# noinspection PyUnusedLocal
@router.put("/role/{rolname}/{id}", response_model=schemas.User)
async def update_user_by_role(
        *,
        db: AsyncSession = Depends(database.get_session),
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(authentication.get_current_active_superuser),
        rolname: str = Query(None),
        id: int = Query(None)
) -> Any:
    """
    Update a user by role.
    """
    user = await crud.user.get_by_id(db, id=id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
