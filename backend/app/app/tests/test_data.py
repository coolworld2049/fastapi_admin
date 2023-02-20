import json
import random
import string

import pytest
from asyncpg import Connection
from asyncpg import UndefinedFunctionError
from faker import Faker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection

from app import crud
from app import schemas
from app.db.init_db import create_all_models, execute_sql_files, create_first_superuser
from app.models.user import User
from app.models.user_role import UserRole
from app.tests.db.session import TestingSessionLocal, test_engine, TestBase, test_pg_database
from app.tests.utils.utils import gen_random_password

fake: Faker = Faker()


async def override_init_db():
    await create_all_models(test_engine)
    await execute_sql_files()
    async with TestingSessionLocal() as db:
        await create_first_superuser(db)


async def truncate_tables():
    asyncpg_conn: Connection = await test_pg_database.get_connection()
    q_truncate = f"""select truncate_tables('postgres')"""
    logger.info(q_truncate)
    try:
        await asyncpg_conn.execute(q_truncate)
    except UndefinedFunctionError:
        await override_init_db()
        await asyncpg_conn.execute(q_truncate)


async def recreate_all():
    async with test_engine.begin() as conn:
        conn: AsyncConnection
        try:
            TestBase.metadata.bind = test_engine
            await conn.run_sync(TestBase.metadata.drop_all, checkfirst=True)
        except Exception as e:
            logger.error(f"metadata.drop_all: {e.args}")
    await override_init_db()


async def create_users(users_count=5):
    ration_teachers_to_students = users_count // 2
    users: list[User] = []
    users_cred_list = []
    role = UserRole.admin.name
    for us in range(users_count):
        logger.info(f"UserCreate: {us + 1}/{users_count}")
        us += 2
        if us >= ration_teachers_to_students:
            role = UserRole.user.name

        password = gen_random_password()
        user_in = schemas.UserCreate(
            email=f"{role}{us}@gmail.com",
            password=password,
            password_confirm=password,
            username=f"{role}{us}{random.randint(1000, 10000)}",
            full_name=fake.name(),
            age=random.randint(18, 25),
            phone="+7" + "".join(random.choice(string.digits) for _ in range(10)),
            role=role,
        )
        users_cred_list.append(
            {user_in.role: {"email": user_in.email, "password": user_in.password}},
        )
        async with TestingSessionLocal() as db:
            user_in_obj = await crud.user.create(db, obj_in=user_in)
            users.append(user_in_obj)

    with open(f"test_api-users_cred_list.json", "w") as wr:
        wr.write(json.dumps(users_cred_list, indent=4))


@pytest.mark.asyncio
async def test_init_db():
    await recreate_all()
    await create_users()
