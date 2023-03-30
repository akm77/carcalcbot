import datetime
import logging
from typing import Optional, Sequence

import aiohttp
from aiohttp.typedefs import StrOrURL
from fake_useragent import UserAgent
from lxml import etree
from sqlalchemy.ext.asyncio import async_sessionmaker

from tgbot.config import Settings
from tgbot.models.costing_data import CurrencyPair
from tgbot.models.db_commands import get_cbr_currency_codes, upsert_currency_pair
from tgbot.services.url_reader import UrlReader, UrlReaderMode
from tgbot.utils.decimals import value_to_decimal

logger = logging.getLogger(__name__)


async def set_cbr_currencies_pair(config: Settings,
                                  db_session: async_sessionmaker,
                                  http_session: aiohttp.ClientSession,
                                  http_proxy: Optional[StrOrURL]) -> Optional[Sequence[CurrencyPair]]:
    logger.info("Start update currency pair from Russia central bank source")
    db_session = db_session
    quote_currency = config.quote_currency
    user_agent = UserAgent().random
    headers = {"User-Agent": user_agent,
               'Content-Type': "application/xml; charset=windows-1251"}
    reader = UrlReader(session=http_session,
                       url="https://www.cbr.ru/scripts/XML_daily.asp",
                       headers=headers,
                       mode=UrlReaderMode.HTML,
                       proxy=http_proxy,
                       logger=logger)
    currencies_xml = await reader.get_raw_data()

    cbr_codes = await get_cbr_currency_codes(session=db_session)
    tree = etree.fromstring(bytes(currencies_xml, encoding="windows-1251"))
    day, month, year = tree.attrib.get("Date").split(".")
    currency_pair_date = datetime.date(int(year), int(month), int(day))
    values = [{"timestamp": currency_pair_date,
               "base_currency_code": code.iso_code_char,
               "quote_currency_code": quote_currency,
               "nominal": int("".join(tree.xpath(f"//*[@ID='{code.cbr_currency_code}']/Nominal/text()"))),
               "value": value_to_decimal("".join(tree.xpath(f"//*[@ID='{code.cbr_currency_code}']/Value/text()")
                                                 ).replace(",", "."),
                                         decimal_places=4)
               } for code in cbr_codes]
    result = await upsert_currency_pair(db_session, values)
    if len(result):
        logger_message = "\n".join([f"{p.nominal} {p.base_currency_code}/{p.quote_currency_code} "
                                    f"{p.value}" for p in result])
    else:
        logger_message = "No currency for update."
    logger.info(logger_message)
    return result
