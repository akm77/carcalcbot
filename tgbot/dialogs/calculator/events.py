from aiogram.types import Message
from aiogram_dialog import ChatEvent, DialogManager
from aiogram_dialog.widgets.common import ManagedWidget
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select

from . import states


async def on_country_changed(event: ChatEvent, widget: ManagedWidget[Select], manager: DialogManager, item_id):
    ctx = manager.current_context()
    ctx.dialog_data.update(country_code=item_id)


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


async def on_enter_price(message: Message, message_input: MessageInput,
                         manager: DialogManager):
    ctx = manager.current_context()
    ctx.dialog_data.update(sell_price=message.text)
    await manager.switch_to(states.CalculatorStates.enter_data)


async def on_enter_volume(message: Message, message_input: MessageInput,
                          manager: DialogManager):
    ctx = manager.current_context()
    ctx.dialog_data.update(engine_volume=message.text)
    await manager.switch_to(states.CalculatorStates.enter_data)


async def on_enter_power(message: Message, message_input: MessageInput,
                         manager: DialogManager):
    ctx = manager.current_context()
    ctx.dialog_data.update(engine_power=message.text)
    await manager.switch_to(states.CalculatorStates.enter_data)
