import asyncio

from asyncpg import Connection
from loguru import logger
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db.session import pg_database

max_tries = 60  # 1 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, 20),
    after=after_log(logger, 30),
)
async def init() -> None:
    try:
        conn: Connection = await pg_database.get_connection()
        logger.info(f'check db version')
        result = await conn.fetch("SELECT * from version()")
        logger.info(f'db version: {result}')
    except Exception as e:
        logger.info(e.args)


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
