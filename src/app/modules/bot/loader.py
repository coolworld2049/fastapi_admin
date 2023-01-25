from aiogram import Dispatcher, Bot

from app.core.config import get_app_settings
from app.db.session import async_session
from app.modules.bot.handlers import start

bot = Bot(token=get_app_settings().BOT_TOKEN)
dispatcher = Dispatcher()
dispatcher.workflow_data.update({'db': async_session()})

dispatcher.include_router(start.router)
