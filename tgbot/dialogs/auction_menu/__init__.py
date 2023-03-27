from aiogram_dialog import Dialog

from . import windows


def auction_menu_dialogs():
    return [
        Dialog(
            windows.auction_menu_window(),
            on_start=None,
            on_process_result=None
        )
    ]
