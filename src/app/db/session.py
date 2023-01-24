from typing import AsyncGenerator

from asyncpg_utils.databases import Database
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_app_settings

Base = declarative_base()

engine: AsyncEngine = engine.create_async_engine(
    get_app_settings().DATABASE_URL.replace('postgresql', 'postgresql+asyncpg'),
    future=True,
    echo=False,
    json_serializer=jsonable_encoder,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

pg_database = Database(get_app_settings().DATABASE_URL)


async def get_async_db() -> AsyncGenerator:
    session: AsyncSession = async_session()  # noqa
    try:
        yield session
    except SQLAlchemyError as sql_ex:
        await session.rollback()
        raise sql_ex
    except HTTPException as http_ex:
        await session.rollback()
        raise http_ex
    else:
        await session.commit()
    finally:
        await session.close()


