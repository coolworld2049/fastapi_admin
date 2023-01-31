from app.core.config import get_app_settings
from asyncpg_utils.databases import Database
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker

Base: DeclarativeBase = declarative_base()


engine: AsyncEngine = create_async_engine(
    get_app_settings().get_postgres_dsn.replace("postgresql", "postgresql+asyncpg"),
    future=True,
    echo=False,
    json_serializer=jsonable_encoder,
)

Base.metadata.bind = engine

SessionLocal = sessionmaker(  # noqa
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

pg_database = Database(get_app_settings().get_postgres_dsn)
