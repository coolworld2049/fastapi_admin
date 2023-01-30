import json
import random
import string
import time

import pytest
from asyncpg import Connection, UndefinedFunctionError
from faker import Faker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app import crud, schemas
from app.db.init_db import init_db
from app.db.session import Base, SessionLocal, engine, pg_database
from app.models.classifiers import UserRole
from app.models.user import User
from app.tests.utils.utils import gen_random_password

fake: Faker = Faker()


@pytest.mark.asyncio
async def test_init_db():
    db: AsyncSession = SessionLocal()
    asyncpg_conn: Connection = await pg_database.get_connection()
    try:
        users_count = 10
        ration_teachers_to_students = users_count // 2

        q_truncate = """select truncate_tables('postgres')"""
        logger.info(q_truncate)
        try:
            await asyncpg_conn.execute(q_truncate)
        except UndefinedFunctionError:
            await init_db()
            await asyncpg_conn.execute(q_truncate)

        async with engine.begin() as conn:
            conn: AsyncConnection
            try:
                Base.metadata.bind = engine
                await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
            except Exception as e:
                logger.error(f"metadata.drop_all: {e.args}")
        await init_db()

        start = time.perf_counter()

        users: list[User] = []
        users_cred_list = []
        role = UserRole.admin.name
        for us in range(users_count):
            logger.info(f"UserCreate: {us}/{users_count}")
            us += 2
            if us >= ration_teachers_to_students:
                role = UserRole.anon.name

            user_in = schemas.UserCreate(
                email=f"{role}{us}@gmail.com",
                password=gen_random_password(us),
                username=f"{role}{us}{random.randint(1000, 10000)}",
                full_name=fake.name(),
                age=random.randint(18, 25),
                phone="+7" + "".join(random.choice(string.digits) for _ in range(10)),
                role=role,
            )
            users_cred_list.append(
                {user_in.role: {"email": user_in.email, "password": user_in.password}}
            )
            user_in_obj = await crud.user.create(db, obj_in=user_in)
            users.append(user_in_obj)

        with open("test_api-users_cred_list.json", "w") as wr:
            wr.write(json.dumps(users_cred_list, indent=4))

        end = time.perf_counter()
        logger.info(f"delta time: {end - start:2}")
    except Exception as e:
        logger.exception(e.args)
