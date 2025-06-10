from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from constants import ADMIN_CHOICES, WELCOME, WELCOME_ADMIN
from keyboards import build_choices_keyboard
from validators import is_admin

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Command /start.

    Start message bot.
    """
    await message.delete()
    if not await is_admin(message.from_user.id):
        await message.answer(
            WELCOME,
        )
    else:
        await message.answer(
            WELCOME_ADMIN,
        )


@router.message(Command('user'))
async def cmd_user(message: Message) -> None:
    """Command /user.

    Start message choices.
    """
    await message.delete()
    await message.answer(
        ADMIN_CHOICES,
        reply_markup=build_choices_keyboard(),
    )
