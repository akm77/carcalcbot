from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from ..dialogs.calculator import states

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.start(states.CalculatorStates.enter_data,
                               data={"started_by": message.from_user.mention_html(),
                                     "country_code": "JP",
                                     "sell_currency_code": "usd",
                                     "fuel_code": "ben",
                                     "uop_code": "ls",
                                     "car_age_code": "age0",
                                     "buyer_type_code": "fiz"},
                               mode=StartMode.RESET_STACK)