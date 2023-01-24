from aiogram import Dispatcher, Bot

from app.core.config import get_app_settings
from app.db.session import async_session
from bot.handlers import start

bot = Bot(token=get_app_settings().BOT_TOKEN)
dp = Dispatcher()
dp['db'] = async_session()

dp.include_router(start.router)
