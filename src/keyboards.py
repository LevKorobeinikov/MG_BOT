from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def build_choices_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения блокировки пользователя."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Добавить',
                    callback_data='add_user',
                ),
                InlineKeyboardButton(
                    text='Удалить',
                    callback_data='remove_user',
                ),
            ],
        ],
    )
