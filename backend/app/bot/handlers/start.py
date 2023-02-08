from __future__ import annotations

from aiogram import Bot
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import MenuButtonWebApp
from aiogram.types import Message
from aiogram.types import WebAppInfo

router = Router()


@router.message(Command(commands=['start']))
async def command_start(message: Message, bot: Bot, base_url: str):
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(
            text='Open Menu', web_app=WebAppInfo(url=f'{base_url}/demo'),
        ),
    )
    await message.answer(
        """Hi!\nSend me any type of message to start.\nOr just send /webview""",
    )


@router.message(Command(commands=['webview']))
async def command_webview(message: Message, base_url: str):
    await message.answer(
        'Good. Now you can try to send it via Webview',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Open Webview', web_app=WebAppInfo(url=f'{base_url}/demo'),
                    ),
                ],
            ],
        ),
    )
