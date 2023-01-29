from typing import AsyncGenerator

from app.db.session import SessionLocal


async def get_session() -> AsyncGenerator:
    session = SessionLocal()
    session.current_user_id = None
    try:
        yield session
    finally:
        await session.close()
