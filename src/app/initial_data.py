import asyncio

from loguru import logger

from app.db.init_db import init_db


def main() -> None:
    logger.info("Creating initial data")
    asyncio.run(init_db())
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
