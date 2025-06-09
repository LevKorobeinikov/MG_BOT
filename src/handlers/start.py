from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from constants import WELCOME

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    """Command /start.

    Start message bot.
    """
    await message.delete()
    await message.answer(
        WELCOME,
    )
