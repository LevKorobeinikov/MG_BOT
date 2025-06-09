import re

CHAT_IDS = [
    -1002503054106,
    -1002551712648,
]
ADMIN_IDS = [
    930229067,
    844295436,
]
USERNAME_PATTERN = re.compile(r'^@?[a-zA-Z0-9_]{5,32}$')
WELCOME = (
    'Добро пожаловать!\nЕсли ты новый сотрудник - жми!\n👇👇👇\n/get_id_user'
)
THIS_IS_CHAT_ID = 'ID этого чата: {message}'
THIS_IS_USER_ID = """
Ваш ID: {user_id}
Username: @{username}
Имя: {full_name}
Отдай эти данные твоему руководителю!
"""
USER_ID_NOT_CORRECT = 'Укажите корректный id сотрудника после команды'
ONLY_ADMIN = 'Только управляющий может это делать!\nКто ты, обезьянка?'
INVITE_PUSH = 'Вам выдали приглашения в чаты:\n'
GEN_INVITE_FOR_CHATS = 'Сгенерированы инвайты для чатов:\n'
USER_REMOVE_ID_NOT_CORRECT = 'Укажите user_id: /remove_user <id>'
BOT_STOP = 'Бот остановлен.'
NO_CHANGE = 'Нет изменений'
