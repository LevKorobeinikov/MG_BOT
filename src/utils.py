async def parse_user_identifier(identifier: str) -> int | None:
    """Преобразует строковый идентификатор (ID или @username) в user_id.

    Возвращает user_id или вызывает исключение при ошибке.
    """
    identifier = identifier.strip()
    if identifier.isdigit():
        return int(identifier)
    return None
