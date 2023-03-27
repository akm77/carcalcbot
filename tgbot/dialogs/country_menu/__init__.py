from aiogram_dialog import Dialog, LaunchMode

from . import windows


def country_menu_dialogs():
    return [
        Dialog(
            windows.country_list_window(),
            windows.country_window(),
            windows.add_country_window(),
            launch_mode=LaunchMode.SINGLE_TOP,
            on_start=None,
            on_process_result=None
        )
    ]
