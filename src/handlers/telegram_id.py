from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from constants import (
    THIS_IS_CHAT_ID,
    THIS_IS_USER_ID,
)

router = Router()


@router.message(Command('get_id_chat'))
async def cmd_show_chat_id(message: Message) -> None:
    """Command /get_id_chat.

    Show chat id.
    """
    await message.delete()
    await message.answer(f'{THIS_IS_CHAT_ID.format(message=message.chat.id)}')


@router.message(Command('get_id_user'))
async def cmd_get_user_id(message: Message) -> None:
    """Command /get_id_user.

    Show user id.
    """
    await message.delete()
    user = message.from_user
    await message.answer(
        THIS_IS_USER_ID.format(
            user_id=user.id,
            full_name=f'{user.first_name} {user.last_name or ""}'.strip(),
        ),
    )
