from typing import Optional

import aiohttp
from aiohttp.typedefs import StrOrURL
from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from tgbot.config import Settings
from tgbot.services.cbr_currency_pair import set_cbr_currencies_pair


def setup_scheduler(scheduler: AsyncIOScheduler,
                    config: Settings,
                    db_session: async_sessionmaker,
                    http_session: aiohttp.ClientSession,
                    http_proxy: Optional[StrOrURL]
                    ):
    set_cbr_currencies_pair_job: Job = scheduler.add_job(set_cbr_currencies_pair,
                                                         'cron',
                                                         hour=23, minute=59, second=59,
                                                         args=(config, db_session, http_session, http_proxy,))
