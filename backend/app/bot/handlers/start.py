from aiogram import Bot
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message, bot: Bot, base_url: str):
    await message.answer(
        """Hi!""",
    )
