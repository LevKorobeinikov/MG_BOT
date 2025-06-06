from constants import ADMIN_IDS


async def is_admin(user_id: int) -> bool:
    """Check admin list."""
    return user_id in ADMIN_IDS
