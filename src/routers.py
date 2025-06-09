from aiogram import Router

from handlers import bot_func_router, start_router

main_router = Router()
main_router.include_router(bot_func_router)
main_router.include_router(start_router)
