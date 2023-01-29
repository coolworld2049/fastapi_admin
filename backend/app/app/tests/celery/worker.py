import asyncio

from sqlalchemy.testing import eq_

from app.core.celery_app import celery_app


@celery_app.task
async def add(x, y):
    return x + y


def test_add_task():
    rst = asyncio.run(add.apply(args=(4, 4)).get())
    eq_(rst, 8)
