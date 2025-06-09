import asyncio

from aiogram import Dispatcher

from config import bot
from constants import BOT_STOP
from routers import main_router

dp = Dispatcher()
dp.include_router(main_router)


async def main() -> None:
    """Start polling bot."""
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(BOT_STOP)
