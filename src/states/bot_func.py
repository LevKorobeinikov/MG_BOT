from aiogram.fsm.state import State, StatesGroup


class UserForm(StatesGroup):
    """FSM-состояния для добавления пользователя."""

    tg_id = State()


class DeleteUserForm(StatesGroup):
    """FSM-состояния для удаления пользователя."""

    tg_id = State()
