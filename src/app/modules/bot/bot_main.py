import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot
from aiogram.types import MenuButtonWebApp, WebAppInfo
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import run_app
from aiohttp.web_app import Application

from app.core.config import get_app_settings
from app.core.logging import InterceptHandler
from app.modules.bot.loader import bot, dispatcher
from app.modules.bot.routes.base import demo_handler, send_message_handler, check_data_handler

logging_level = logging.INFO

logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        InterceptHandler(),
        RotatingFileHandler('access.log', maxBytes=get_app_settings().log_file_max_bytes, backupCount=1)
    ])


async def bot_main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot, skip_updates=True, allowed_updates=dispatcher.resolve_used_update_types())


def bot_webapp_main():
    async def on_startup(_bot: Bot, base_url: str):
        await _bot.set_webhook(f"{base_url}/webhook")
        await _bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open Menu", web_app=WebAppInfo(url=f"{base_url}/demo"))
        )

    dispatcher["base_url"] = get_app_settings().APP_BASE_URL
    dispatcher.startup.register(on_startup)

    app = Application()
    app["bot"] = bot

    app.router.add_get("/demo", demo_handler)
    app.router.add_post("/demo/checkData", check_data_handler)
    app.router.add_post("/demo/sendMessage", send_message_handler)
    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
    ).register(app, path="/webhook")
    setup_application(app, dispatcher, bot=bot)

    run_app(app, host="127.0.0.1", port=8081)


if __name__ == '__main__':
    try:
        asyncio.run(bot_main())
    except Exception as e:  # noqa
        pass
