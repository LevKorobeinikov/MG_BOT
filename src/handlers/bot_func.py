from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import bot
from constants import (
    CHAT_IDS,
    GEN_INVITE_FOR_CHATS,
    GIVE_ME_TG_ID,
    INVITE_PUSH,
    NO_CHANGE,
    ONLY_ADMIN,
    USER_ID_NOT_CORRECT,
)
from states.bot_func import DeleteUserForm, UserForm
from validators import is_admin

router = Router()


async def get_user_id_check_command(
    message: Message,
) -> None:
    """Take user_id from command and checks for admin rights."""
    if not await is_admin(message.from_user.id):
        await message.answer(ONLY_ADMIN)
        return None
    user_input = message.text.strip()
    if not user_input:
        await message.answer(USER_ID_NOT_CORRECT)
        return None
    try:
        return int(user_input)
    except ValueError:
        await message.answer('Неверный формат ID. Используйте только цифры')
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
        except TelegramBadRequest as error:
            errors.append(f'{chat_id}: {error.message}')
    if invite_links:
        try:
            await bot.send_message(
                user_id,
                INVITE_PUSH + '\n' + '\n\n'.join(invite_links),
            )
        except TelegramBadRequest as error:
            errors.append(f'send_message to {user_id}: {error.message}')
    return invite_links, errors


@router.callback_query(F.data.startswith('add_user'))
async def cmd_add_user(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Command /add_user."""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        GIVE_ME_TG_ID,
    )
    await state.set_state(UserForm.tg_id)


@router.message(UserForm.tg_id)
async def proc_tg_id(
    message: Message,
    state: FSMContext,
) -> None:
    """Take ID and adds to chats."""
    if message.text == '/cancel':  # Проверяем отмену
        await cmd_cancel(message, state)
        return
    report: List = []
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
    await message.answer(
        '\n'.join(report) if report else 'Ничего не сделано',
    )
    await state.clear()
    await message.delete()


@router.callback_query(F.data.startswith('remove_user'))
async def cmd_remove_user(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Command /remove_user."""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        GIVE_ME_TG_ID,
    )
    await state.set_state(DeleteUserForm.tg_id)


@router.message(DeleteUserForm.tg_id)
async def proc_tg_id_remove(
    message: Message,
    state: FSMContext,
) -> None:
    """Take ID and deletes from chats."""
    if message.text == '/cancel':  # Проверяем отмену
        await cmd_cancel(message, state)
        return
    user_id = await get_user_id_check_command(message)
    success, not_found, errors = [], [], []
    report: List = []
    for chat_id in CHAT_IDS:
        try:
            await bot.ban_chat_member(chat_id, user_id)
            success.append(chat_id)
        except TelegramBadRequest as error:
            desc = error.args[0].lower()
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
    await state.clear()
    await message.delete()


@router.message(Command('cancel'))
async def cmd_cancel(
    message: Message,
    state: FSMContext,
) -> None:
    """Cancel all."""
    await state.clear()
    await message.answer('Все действия отменены.')
