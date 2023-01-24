# noqa:WPS201

from asyncpg import Connection
from fastapi import Depends, HTTPException
from fastapi.logger import logger
from jose import jwt, JWTError
from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import crud, schemas
from app.api.api_v1.dependencies import database
from app.core.config import get_app_settings
from app.models.user import User
from app.services.jwt import oauth2Scheme


async def get_current_user(
        db: AsyncSession = Depends(database.get_session),
        token: str = Depends(oauth2Scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            get_app_settings().SECRET_KEY,
            algorithms=[get_app_settings().ALGORITHM],
            options={"verify_aud": False},
        )
        subject: str = payload.get("sub")
        scopes: str = payload.get("scopes")
        if not subject:
            raise credentials_exception
        token_data = schemas.TokenPayload(sub=subject, scopes=scopes)
    except JWTError:
        raise credentials_exception
    if not token_data.sub.isdigit():
        raise credentials_exception
    user = await crud.user.get_by_id(db=db, id=int(token_data.sub))
    if user is None:
        raise credentials_exception

    db_user = user.username
    await get_session_user(db)
    await reset_session_user(db)
    await get_session_user(db)
    check_result = await check_rolname(db, db_user, user)
    if not check_result:
        await create_user_in_role(db, user, db_user)
    await reset_session_user(db)
    await get_session_user(db)
    await set_session_user(db, db_user)
    await get_session_user(db)
    return user


async def check_rolname(db: AsyncSession, db_user: str, current_user: User):
    if not current_user.is_active:
        raise HTTPException(400, 'user is not active')
    if not current_user.username == db_user:
        raise HTTPException(400, 'username not valid')
    check_q = """select rolname from pg_roles where rolname = :db_user"""
    check_q_result: Result = await db.execute(text(check_q), {'db_user': db_user.lower()})

    check_result = check_q_result.fetchall()
    if get_app_settings().DEBUG:
        logger.info(f"check_rolname: {f'{db_user} role exist' if check_result else f'{db_user} role not exist'}")
    return check_result


async def create_user_in_role(db: AsyncSession, current_user: User, db_user: str):
    create_db_user_q = '''select create_user_in_role(:db_user, :hashed_password, :role)'''
    params = {
        'db_user': db_user.lower(),
        'hashed_password': current_user.hashed_password,
        'role': current_user.role
    }
    await db.execute(text(create_db_user_q), params=params)
    await db.commit()
    if get_app_settings().DEBUG:
        logger.info(f'CREATE_user_in_role: {create_db_user_q}')


async def drop_user_in_role(db: AsyncSession | Connection, db_user: str):
    drop_db_user_q = """drop user """ + db_user.lower()
    if isinstance(db, Connection):
        await db.execute(drop_db_user_q)
    elif isinstance(db, AsyncSession):
        await db.execute(text(drop_db_user_q))
    if get_app_settings().DEBUG:
        logger.info(f'DROP_user_in_role: {db_user}')


async def get_session_user(db: AsyncSession):
    check_session_role_q = """select session_user, current_user"""
    check_session_role_q_result: Result = await db.execute(text(check_session_role_q))
    if get_app_settings().DEBUG:
        logger.info(f'get_session_user: {check_session_role_q_result.scalar()}')


async def set_session_user(db: AsyncSession, db_user: str):
    set_db_user_q = """set session authorization """ + db_user.lower()
    if get_app_settings().DEBUG:
        logger.info(f'SET_session_user: {db_user}')
    await db.execute(text(set_db_user_q))


async def reset_session_user(db: AsyncSession):
    reset_q = '''reset session authorization'''
    if get_app_settings().DEBUG:
        logger.info(f'RESET_session_user')
    await db.execute(text(reset_q))


async def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
        current_user: User = Depends(get_current_user),
) -> User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
