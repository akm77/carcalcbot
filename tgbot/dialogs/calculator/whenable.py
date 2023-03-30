from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable


def check_required_fields(data: Dict, widget: Whenable, manager: DialogManager):
    dialog_data = data.get("dialog_data")
    start_data = data.get("start_data")
    engine_volume = dialog_data.get("engine_volume") or 0
    engine_power = dialog_data.get("engine_power") or 0
    sell_price = dialog_data.get("sell_price") or 0
    buyer_type_code = dialog_data.get("buyer_type_code") or start_data.get("buyer_type_code")
    return engine_volume and engine_power and sell_price if buyer_type_code == "entity" else engine_volume and sell_price


def is_legal_entity(data: Dict, widget: Whenable, manager: DialogManager):
    dialog_data = data.get("dialog_data")
    start_data = data.get("start_data")
    buyer_type_code = dialog_data.get("buyer_type_code") or start_data.get("buyer_type_code")
    return buyer_type_code == "entity"
