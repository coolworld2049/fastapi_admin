from aiogram import types, Router
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas

router = Router()


@router.message(CommandStart())
async def start_cmd(message: types.Message, db: AsyncSession):
    users, total = await crud.user.get_multi(db)
    text = "\n".join("  ".join((f"<b>{k}</b>", str(v))) for k, v in
                     schemas.User(**users[0].to_dict()) if v)
    await message.answer(text, parse_mode='HTML')
