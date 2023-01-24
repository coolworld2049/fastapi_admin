import logging
import pathlib

from asyncpg import Connection
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection

from app import crud, schemas
from app.core.config import get_app_settings
from app.db.session import engine, async_session, pg_database, Base
from app.models.classifiers import UserRole


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
    db = async_session()
    await create_all()
    for sql_f in list(pathlib.Path(f"{pathlib.Path().resolve()}/db/sql/").iterdir()):
        if not sql_f.is_dir():
            await exec_sql_file(sql_f, await pg_database.get_connection())
            logger.info(sql_f.name)
    super_user = await crud.user.get_by_email(db, email=get_app_settings().FIRST_SUPERUSER_EMAIL)
    if not super_user:
        user_in_admin = schemas.UserCreate(
            email=get_app_settings().FIRST_SUPERUSER_EMAIL,
            password=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name='Super User',
            username=get_app_settings().FIRST_SUPERUSER_USERNAME,
            role=UserRole.admin.name
        )
        await crud.user.create(db, obj_in=user_in_admin)
