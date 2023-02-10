import asyncio

from app.tests.test_data import create_users, recreate_all


async def main():
    await recreate_all()
    await create_users(50)


if __name__ == "__main__":
    asyncio.run(main())
