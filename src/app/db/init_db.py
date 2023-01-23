import logging
import pathlib

from asyncpg import Connection
from sqlalchemy.ext.asyncio import AsyncConnection

from app import crud
from app.models import schemas
from app.core.config import get_app_settings
from app.db import classifiers
from app.db.session import engine, AsyncSessionFactory, pg_database, Base


async def exec_sql_file(path: pathlib.Path, conn: Connection):
    try:
        with open(path, encoding='utf-8') as rf:
            res = await conn.execute(rf.read())
            logging.info(f'{path.name}: {res}')
    except Exception as e:
        logging.error(f'{path.name}: {e.args}')


async def create_all():
    async with engine.begin() as conn:
        conn: AsyncConnection
        try:
            Base.metadata.bind = engine
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logging.warning(e)


async def init_db():
    db = AsyncSessionFactory()
    await create_all()
    for sql_f in list(pathlib.Path(f"{pathlib.Path().cwd()}/db/sql/").iterdir()):
        if not sql_f.is_dir():
            await exec_sql_file(sql_f, await pg_database.get_connection())
    super_user = await crud.user.get_by_email(db, email=get_app_settings().FIRST_SUPERUSER_EMAIL)
    if not super_user:
        user_in_admin = schemas.UserCreate(
            email=get_app_settings().FIRST_SUPERUSER_EMAIL,
            password=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name='Super User',
            username=get_app_settings().FIRST_SUPERUSER_USERNAME,
            role=classifiers.UserRole.admin.name
        )
        await crud.user.create(db, obj_in=user_in_admin)
