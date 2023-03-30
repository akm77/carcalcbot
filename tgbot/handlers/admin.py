from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from tgbot.filters.admin import AdminFilter
from ..dialogs.calculator import states

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.CalculatorStates.enter_data,
                               data={"started_by": message.from_user.mention_html(),
                                     "country_code": "JP",
                                     "sell_currency_code": "JPY",
                                     "fuel_code": "gasoline",
                                     "uop_code": "hp",
                                     "car_age_code": "age0",
                                     "buyer_type_code": "private"},
                               mode=StartMode.RESET_STACK)



