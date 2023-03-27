from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tgbot.config import Settings
from tgbot.models.db_commands import get_last_pairs
from tgbot.services.cbr_currency_pair import set_cbr_currencies_pair

cbr_router = Router()


@cbr_router.message(Command("cbr"))
async def cbr_get(message: types.Message, state: FSMContext, **data):
    config: Settings = data.get("config")
    db_session = data.get("db_session")
    http_session = data.get("http_session")
    http_proxy = data.get("http_proxy")

    result = await set_cbr_currencies_pair(config,
                                           db_session,
                                           http_session,
                                           http_proxy)

    if len(result):
        message_text = f"Курсы вапют на <b>{result[0].timestamp: %d.%m.%Y}</b>\n"
        message_text += "\n".join(
            [f"<code>{p.nominal:5d} {p.base_currency_code}/{p.quote_currency_code}</code> "
             f"{p.value}" for p in result])
    else:
        message_text = "Нет доступных для обновления курсов валют.\n"
        result = await get_last_pairs(db_session, base_currency=config.form_currencies)
        if len(result):
            message_text += f"Курсы вапют на <b>{result[0].timestamp: %d.%m.%Y}</b>\n"
            message_text += "\n".join(
                [f"<code>{p.nominal:5d} {p.base_currency_code}/{p.quote_currency_code}</code> "
                 f"{p.value}" for p in result])
    await message.answer(message_text)
