import asyncio
import logging
from typing import Any

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog.widgets.text import setup_jinja
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import settings
from tgbot.dialogs import setup_dialogs
from tgbot.handlers.admin import admin_router
from tgbot.handlers.cbr import cbr_router
from tgbot.handlers.dict_setup import country_router, auction_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware, UserDBMiddleware
from tgbot.models.base import create_db_session
from tgbot.services import broadcaster
from tgbot.services.aps_scheduler import setup_scheduler
from tgbot.utils.calculation import formatvalue

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Bot started")


def register_global_middlewares(dp: Dispatcher, config, db_session, http_session, http_proxy):
    dp.my_chat_member.outer_middleware(ConfigMiddleware(config, db_session, http_session, http_proxy))
    dp.message.outer_middleware(ConfigMiddleware(config, db_session, http_session, http_proxy))
    dp.message.outer_middleware(UserDBMiddleware())
    dp.callback_query.outer_middleware(ConfigMiddleware(config, db_session, http_session, http_proxy))
    dp.callback_query.outer_middleware(UserDBMiddleware())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    config = settings
    if config.use_redis:
        storage = RedisStorage.from_url(config.redis_dsn, key_builder=DefaultKeyBuilder(with_bot_id=True,
                                                                                        with_destiny=True))
    else:
        storage = MemoryStorage()

    http_proxy = config.proxy if config.use_proxy else None

    db_session = await create_db_session(config.db_dialect, config.db_name, config.db_user,
                                         config.db_pass.get_secret_value(), config.db_host, config.db_echo)
    http_session = aiohttp.ClientSession()
    bot = Bot(token=config.bot_token.get_secret_value(), parse_mode='HTML')
    dp = Dispatcher(storage=storage)
    dp["http_session"] = http_session
    dp.shutdown.register(on_shutdown)
    setup_jinja(bot=bot, filters={"formatvalue": formatvalue}, enable_async=True)
    setup_dialogs(dp)

    for router in [
        admin_router,
        user_router,
        country_router,
        auction_router,
        cbr_router
        # echo_router
    ]:

        dp.include_router(router)

    register_global_middlewares(dp, config, db_session, http_session, http_proxy)
    scheduler: AsyncIOScheduler = AsyncIOScheduler()
    setup_scheduler(scheduler, config, db_session, http_session, http_proxy)
    await on_startup(bot, config.admins)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def on_shutdown(bot: Bot, **kwargs: Any):
    dp = kwargs.get('dispatcher')
    http_session = dp.get("http_session")
    await http_session.close() if http_session else None


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
