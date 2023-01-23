from app.db.session import AsyncSessionFactory


async def get_session():
    async with AsyncSessionFactory() as session:
        yield session
