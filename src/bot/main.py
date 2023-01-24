import asyncio
import logging
import sys
from logging.handlers import RotatingFileHandler

from loguru import logger

from app.core.config import get_app_settings
from app.core.logging import InterceptHandler
from bot.loader import bot, dp

logging_level = logging.INFO


logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        InterceptHandler(),
        RotatingFileHandler('access.log', maxBytes=get_app_settings().log_file_max_bytes, backupCount=1)
    ])
logging_logger = logging.getLogger(__name__)
logging_logger.handlers = [InterceptHandler(level=logging_level)]
logger.configure(handlers=[{"sink": sys.stdout, "level": logging_level}])


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(e.args)
