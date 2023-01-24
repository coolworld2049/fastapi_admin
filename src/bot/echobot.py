import logging

import asyncpg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import escape_md

from app import crud, schemas
from app.core.config import get_app_settings
from app.db.session import async_session

API_TOKEN = '5654331350:AAGLWJSUXdesNc9G-TvbK4lr50pr0XdKuds'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
bot['db'] = async_session()
dp = Dispatcher(bot)
settings = get_app_settings()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    users, total = await crud.user.get_multi(bot.get('db'))
    text = "\n".join(escape_md("  ").join((f"***{escape_md(k)}***", escape_md(str(v)))) for k, v in
                     schemas.User(**users[0].to_dict()) if v)
    await message.reply(
        text,
        parse_mode=types.ParseMode.MARKDOWN_V2
    )


async def on_startup(_):
    bot['pool'] = await asyncpg.create_pool(
        str(settings.DATABASE_URL),
        min_size=settings.min_connection_count,
        max_size=settings.max_connection_count,
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
