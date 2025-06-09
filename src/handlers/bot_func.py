from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from config import bot
from constants import (
    CHAT_IDS,
    GEN_INVITE_FOR_CHATS,
    INVITE_PUSH,
    NO_CHANGE,
    ONLY_ADMIN,
    THIS_IS_CHAT_ID,
    THIS_IS_USER_ID,
    USER_ID_NOT_CORRECT,
)
from utils import parse_user_identifier
from validators import is_admin

router = Router()


async def get_user_id_check_command(
    message: Message,
) -> None:
    """Take user_id from command and checks for admin rights."""
    if not await is_admin(message.from_user.id):
        await message.reply(ONLY_ADMIN)
        return None
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply(USER_ID_NOT_CORRECT)
        return None
    try:
        return await parse_user_identifier(parts[1].strip())
    except ValueError as error:
        await message.reply(str(error))
    except Exception as error:
        await message.reply(f'Неизвестная ошибка: {str(error)}')
        return None


async def send_invites_to_user(user_id: int) -> Tuple[List[str], List[str]]:
    """Send invite links to user for all chats."""
    invite_links = []
    errors = []
    for chat_id in CHAT_IDS:
        try:
            await bot.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                only_if_banned=True,
            )
            invite = await bot.create_chat_invite_link(
                chat_id=chat_id,
                expire_date=datetime.now(timezone.utc) + timedelta(days=2),
                creates_join_request=False,
            )
            invite_links.append(invite.invite_link)
        except TelegramBadRequest as e:
            errors.append(f'{chat_id}: {e.message}')
    if invite_links:
        try:
            await bot.send_message(
                user_id,
                INVITE_PUSH + '\n' + '\n'.join(invite_links),
            )
        except TelegramBadRequest as e:
            errors.append(f'send_message to {user_id}: {e.message}')
    return invite_links, errors


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
            username=user.username or '',
            full_name=f'{user.first_name} {user.last_name or ""}'.strip(),
        ),
    )


@router.message(Command('add_user'))
async def cmd_add_user(message: Message) -> None:
    """Command /add_user <user_id>.

    Gen invite for chats and send them for user.
    """
    await message.delete()
    report = []
    user_id = await get_user_id_check_command(message)
    if not user_id:
        return
    invite_links, errors = await send_invites_to_user(user_id)
    if invite_links:
        report.append(GEN_INVITE_FOR_CHATS)
        report.extend(invite_links)
    if errors:
        report.append('\nОшибки:')
        report.extend(errors)
    await message.answer('\n'.join(report) if report else 'Ничего не сделано')


@router.message(Command('remove_user'))
async def cmd_remove_user(message: Message) -> None:
    """Command /remove_user <user_id>.

    Delete user from chats.
    """
    await message.delete()
    user_id = await get_user_id_check_command(message)
    success, not_found, errors = [], [], []
    report = []
    for chat_id in CHAT_IDS:
        try:
            await bot.ban_chat_member(chat_id, user_id)
            success.append(chat_id)
        except TelegramBadRequest as e:
            desc = e.args[0].lower()
            if 'not participant' in desc or 'user not found' in desc:
                not_found.append(chat_id)
            else:
                errors.append(f'{chat_id} ({desc})')
    if success:
        report.append(f'Удалён из:\n{", ".join(map(str, success))}')
    if not_found:
        report.append(f'Не найден в:\n{", ".join(map(str, not_found))}')
    if errors:
        report.append(f'Ошибки:\n{", ".join(errors)}')
    await message.answer('\n'.join(report) if report else NO_CHANGE)
