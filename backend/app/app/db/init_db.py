import pathlib

from asyncpg import Connection
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app import schemas
from app.core.config import get_app_settings
from app.db.session import Base
from app.db.session import SessionLocal
from app.db.session import engine
from app.db.session import pg_database
from app.models.user_role import UserRole


async def execute_sql_files(path: pathlib.Path, conn: Connection):
    try:
        with open(path, encoding="utf-8") as rf:
            res = await conn.execute(rf.read())
            logger.info(f"{path.name}: {res}")
    except Exception as e:
        logger.info(f"{path.name}: {e.args}")


async def create_all_models(drop=False):
    async with engine.begin() as conn:
        m = Base.metadata
        await conn.run_sync(m.create_all if not drop else m.drop_all)


async def create_first_superuser(db: AsyncSession):
    super_user = await crud.user.get_by_email(
        db,
        email=get_app_settings().FIRST_SUPERUSER_EMAIL,
    )
    if not super_user:
        user_in_admin = schemas.UserCreate(
            email=get_app_settings().FIRST_SUPERUSER_EMAIL,
            password=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            password_confirm=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="No Name",
            username=get_app_settings().FIRST_SUPERUSER_USERNAME,
            role=UserRole.admin.name,
            verified=True,
        )
        super_user = await crud.user.create(db, obj_in=user_in_admin)
        logger.info("created")
    else:
        logger.info("first superuser already exists")
    return super_user


async def init_db():
    # await create_all_models(drop=True)
    await create_all_models()
    conn: Connection = await pg_database.get_connection()
    for sql_f in pathlib.Path(
        pathlib.Path(__file__).parent.__str__() + "/sql",
    ).iterdir():
        if not sql_f.is_dir():
            await execute_sql_files(sql_f, conn)
    await conn.close()
    async with SessionLocal() as db:
        await create_first_superuser(db)
