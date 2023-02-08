from __future__ import annotations

from aiogram import Bot
from aiogram import Dispatcher
from app.core.config import get_app_settings
from app.db.session import SessionLocal
from bot.handlers import start

bot = Bot(token=get_app_settings().BOT_TOKEN)
dispatcher = Dispatcher()
dispatcher.workflow_data.update(
    {'db': SessionLocal(), 'base_url': get_app_settings().DOMAIN},
)
dispatcher.include_router(start.router)
