import asyncio
import json
import random
import string
import time

from asyncpg import Connection, UndefinedFunctionError
from faker import Faker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import crud, schemas
from app.db.init_db import init_db
from app.db.session import pg_database, async_session, engine
from app.models.classifiers import UserRole
from app.models.user import User

fake: Faker = Faker()


def gen_rand_password(number: int, rnd_str_length: int = 4):
    r_str = ''.join(random.choice(string.ascii_letters) for _ in range(rnd_str_length)).capitalize()
    return f"{''.join(random.choice(string.ascii_letters) for _ in range(rnd_str_length)).capitalize()}" \
           f"{r_str}{number}{number * 2}" \
           f"{''.join(random.choice(string.ascii_letters) for _ in range(rnd_str_length)).capitalize()}" \
           f"{random.choice(['!', '@', '#', '$', '&', '*'])}"


async def init_db_test():
    db: AsyncSession = async_session()
    asyncpg_conn: Connection = await pg_database.get_connection()
    try:
        users_count = 50
        ration_teachers_to_students = users_count // 2

        q_truncate = f'''select truncate_tables('postgres')'''
        logger.info(q_truncate)
        try:
            await asyncpg_conn.execute(q_truncate)
        except UndefinedFunctionError:
            await init_db()
            await asyncpg_conn.execute(q_truncate)

        async with engine.begin() as conn:
            conn: AsyncConnection
            try:
                SQLModel.metadata.bind = engine
                await conn.run_sync(SQLModel.metadata.drop_all, checkfirst=True)
            except Exception as e:
                logger.error(f'metadata.drop_all: {e.args}')
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
                email=f'{role}{us}@gmail.com',
                password=gen_rand_password(us),
                username=f'{role}{us}{random.randint(1000, 10000)}',
                full_name=fake.name(),
                age=random.randint(18, 25),
                phone='+7' + ''.join(random.choice(string.digits) for _ in range(10)),
                role=role
            )
            users_cred_list.append({
                user_in.role: {
                    'email': user_in.email,
                    'password': user_in.password
                }
            })
            user_in_obj = await crud.user.create(db, obj_in=user_in)
            users.append(user_in_obj)

        with open(f"users_cred_list.json", 'w') as wr:
            wr.write(json.dumps(users_cred_list, indent=4))

        end = time.perf_counter()
        logger.info(f"gen process_time: {end - start:2}")
    except Exception as e:
        logger.exception(e.args)


if __name__ == '__main__':
    asyncio.run(init_db_test())
