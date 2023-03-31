import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from tgbot.config import Settings
from tgbot.utils.calculation import cost_calculation

logger = logging.getLogger(__name__)


async def on_click_calculate(callback: CallbackQuery, button: Button, manager: DialogManager):
    manager.show_mode = ShowMode.SEND
    dialog_data = manager.current_context().dialog_data
    config: Settings = manager.middleware_data.get("config")
    session = manager.middleware_data.get('db_session')
    cost_calculation_text = await cost_calculation(config=config, db_session=session, data=dialog_data)
    dialog_data.update(cost_calculation_text=cost_calculation_text)
