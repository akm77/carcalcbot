import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from ..config import Settings
from ..dialogs.calculator import states
from ..services.cbr_currency_pair import set_cbr_currencies_pair

logger = logging.getLogger(__name__)
user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, dialog_manager: DialogManager, **data):
    config: Settings = data.get("config")
    db_session = data.get("db_session")
    http_session = data.get("http_session")
    http_proxy = data.get("http_proxy")

    result = await set_cbr_currencies_pair(config,
                                           db_session,
                                           http_session,
                                           http_proxy)
    if len(result):
        logger.info(f"Установлены курсы вапют на {result[0].timestamp: %d.%m.%Y}")

    await dialog_manager.start(states.CalculatorStates.enter_data,
                               data={"started_by": message.from_user.mention_html(),
                                     "country_code": "JP",
                                     "sell_currency_code": "JPY",
                                     "fuel_code": "gasoline",
                                     "uop_code": "hp",
                                     "car_age_code": "age0",
                                     "buyer_type_code": "private"},
                               mode=StartMode.RESET_STACK)
