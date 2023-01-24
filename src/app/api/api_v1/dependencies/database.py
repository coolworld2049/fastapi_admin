from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session


async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        session: AsyncSession
        session.current_user_id = None
        yield session
