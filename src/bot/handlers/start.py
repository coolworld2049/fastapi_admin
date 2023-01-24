from aiogram import types, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api.api_v1.dependencies.database import get_session

router = Router()


@router.message(commands=['start'])
async def start_cmd(message: types.Message, db: AsyncSession):
    users, total = await crud.user.get_multi(db)
    text = "\n".join("  ".join((f"<b>{k}</b>", str(v))) for k, v in
                     schemas.User(**users[0].to_dict()) if v)
    await message.answer(text, parse_mode='HTML')
