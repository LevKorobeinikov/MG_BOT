import asyncio
from datetime import datetime, timedelta, timezone

from aiogram import Dispatcher, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

from config import bot
from constants import CHAT_IDS
from utils import parse_user_identifier
from validators import is_admin

dp = Dispatcher()
router = Router()
dp.include_router(router)


@router.message(Command('start'))
async def cmd_start(message: Message) -> None:
    """Start message."""
    await message.answer(
        'Добро пожаловать!\nЕсли ты новый сотрудник - жми сюда:  /get_id_user',
    )


@router.message(Command('get_id_chat'))
async def cmd_show_chat_id(message: Message) -> None:
    """Show chat id."""
    await message.answer(f'ID этого чата: {message.chat.id}')


@router.message(Command('get_id_user'))
async def cmd_get_user_id(message: Message) -> None:
    """Show user id."""
    user = message.from_user
    await message.answer(
        f'Ваш ID: {user.id}\n'
        f'Username: @{user.username or ""}\n'
        f'Имя: {user.first_name} {user.last_name or ""}\n'
        f'Отдай эти данные твоему руководителю!',
    )


@router.message(Command('add_user'))
async def cmd_add_user(message: Message) -> None:
    """Команда /add_user <user_id>.

    Генерируем инвайт-линк для каждого чата и шлём его пользователю.
    """
    if not await is_admin(message.from_user.id):
        await message.reply('Только админ может выдавать инвайты')
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply(
            'Укажите user_id: /add_user <identifier>',
        )
        return
    identifier = parts[1].strip()
    try:
        user_id = await parse_user_identifier(identifier)
    except ValueError as error:
        await message.reply(str(error))
        return
    except Exception as error:
        await message.reply(f'Неизвестная ошибка: {str(error)}')
        return
    invite_links = []
    errors = []
    report = []
    for chat_id in CHAT_IDS:
        try:
            await bot.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                only_if_banned=True,
            )
            expire_dt = datetime.now().replace(
                tzinfo=timezone.utc,
            ) + timedelta(days=2)
            invite = await bot.create_chat_invite_link(
                chat_id=chat_id,
                expire_date=expire_dt,
                creates_join_request=False,
            )
            invite_links.append((invite.invite_link))
        except TelegramBadRequest as e:
            errors.append(f'{chat_id}: {e.message}')
    if invite_links:
        text = ['Вам выдали приглашения в чаты:\n']
        for link in invite_links:
            text.append(f'{link}')
        try:
            await bot.send_message(user_id, '\n'.join(text))
        except TelegramBadRequest as e:
            errors.append(f'send_message to {user_id}: {e.message}')
        report.append('Сгенерированы инвайты для чатов:\n')
        report += [f'{link}' for link in invite_links]
    if errors:
        report.append('\nОшибки:')
        report += errors
    await message.answer('\n'.join(report))


@router.message(Command('remove_user'))
async def cmd_remove_user(message: Message) -> None:
    """Delete user from chat."""
    if not await is_admin(message.from_user.id):
        await message.reply(
            'Команда только для администраторов! Ты не пройдешь!',
        )
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply(
            'Укажите user_id: /remove_user <identifier>',
        )
        return
    identifier = parts[1].strip()
    try:
        user_id = await parse_user_identifier(identifier)
    except ValueError as error:
        await message.reply(str(error))
        return
    except Exception as error:
        await message.reply(f'Неизвестная ошибка: {str(error)}')
        return
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
    await message.answer('\n'.join(report) if report else 'Нет изменений')


async def main() -> None:
    """Запускает поллинг бота."""
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен.')
