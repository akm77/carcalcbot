from aiogram import Dispatcher
from aiogram_dialog import DialogRegistry

from . import calculator, country_menu, auction_menu


def setup_dialogs(dp: Dispatcher):
    registry = DialogRegistry()
    for dialog in [
        *calculator.calculator_dialogs(),
        *country_menu.country_menu_dialogs(),
        # *auction_menu.auction_menu_dialogs()
    ]:
        registry.register(dialog)  # register a dialog

    registry.setup_dp(dp)
