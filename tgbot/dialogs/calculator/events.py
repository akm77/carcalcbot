from aiogram.types import Message
from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.widgets.common import ManagedWidget
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select

from . import states, constants
from ...models.db_commands import get_country_currency
from ...utils.decimals import check_digit_value


async def on_country_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(country_code=item_id)
    if item_id == "JP":
        ctx.dialog_data.update(freight_type="direct")
    session = manager.middleware_data.get('db_session')
    currency = await get_country_currency(session=session, country=item_id)
    select_sell_currency_kbd = manager.find(constants.CalculatorForm.SELECT_SELL_CURRENCY)
    await select_sell_currency_kbd.set_checked(item_id=currency.currency_iso_code_char)


async def on_car_age_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(car_age_code=item_id)


async def on_sell_currency_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(sell_currency_code=item_id)


async def on_fuel_type_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(fuel_code=item_id)


async def on_uop_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(uop_code=item_id)


async def on_buyer_type_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(buyer_type_code=item_id)


async def on_freight_type_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(freight_type=item_id)
    if item_id == "indirect":
        ctx.dialog_data.update(buyer_type_code="private")


async def on_enter_price(message: Message, message_input: MessageInput,
                         manager: DialogManager):
    ctx = manager.current_context()
    try:
        sell_price = check_digit_value(message.text, type_factory=int)
        ctx.dialog_data.update(sell_price=sell_price)
    except ValueError:
        message_text = f"Ошибка ввода {message.text}, необходимо целое число\n"
        await message.answer(message_text)
        return
    await manager.switch_to(states.CalculatorStates.enter_data)


async def on_enter_volume(message: Message, message_input: MessageInput,
                          manager: DialogManager):
    ctx = manager.current_context()
    try:
        engine_volume = check_digit_value(message.text, type_factory=int)
        ctx.dialog_data.update(engine_volume=engine_volume)
    except ValueError:
        message_text = f"Ошибка ввода {message.text}, необходимо целое число\n"
        await message.answer(message_text)
        return
    await manager.switch_to(states.CalculatorStates.enter_data)


async def on_enter_power(message: Message, message_input: MessageInput,
                         manager: DialogManager):
    ctx = manager.current_context()
    try:
        engine_power = check_digit_value(message.text, type_factory=int)
        ctx.dialog_data.update(engine_power=engine_power)
    except ValueError:
        message_text = f"Ошибка ввода {message.text}, необходимо целое число\n"
        await message.answer(message_text)
        return
    await manager.switch_to(states.CalculatorStates.enter_data)
