import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from fake_useragent import UserAgent

from tgbot.services.url_reader import UrlReader, UrlReaderMode

logger = logging.getLogger(__name__)


async def on_click_calculate(callback: CallbackQuery, button: Button, manager: DialogManager):
    ctx = manager.current_context()
    dialog_data = ctx.dialog_data
    message_text = "Калькуляция"
    await callback.message.answer(message_text)
