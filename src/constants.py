import re

CHAT_IDS = [
    -1002503054106,
]
ADMIN_IDS = [
    930229067,
    844295436,
]
USERNAME_PATTERN = re.compile(r'^@?[a-zA-Z0-9_]{5,32}$')
