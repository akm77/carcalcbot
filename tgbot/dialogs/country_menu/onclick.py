from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import Button

from . import states
# from ...models.db_commands import delete_country_from_db


async def on_select_country(callback: CallbackQuery,
                            widget: Widget,
                            manager: DialogManager,
                            data: str):
    ctx = manager.current_context()
    iso3_code = data
    ctx.dialog_data.update(iso3_code=iso3_code)
    await manager.switch_to(states.CountryMenuStates.edit_country)


async def on_click_delete_country(callback: CallbackQuery,
                                  button: Button,
                                  manager: DialogManager):
    db_session = manager.middleware_data.get("db_session")
    ctx = manager.current_context()
    iso3_code = ctx.dialog_data.get("iso3_code")
    deleted_country = await delete_country_from_db(session=db_session,
                                                   iso3_code=iso3_code)
    if deleted_country:
        message_text = f"Entry {deleted_country.name_short} deleted successfully!"
        await callback.message.answer(message_text)
        ctx.dialog_data.pop("iso3_code")
        await manager.switch_to(states.CountryMenuStates.select_country)
    else:
        await callback.message.answer("Entry was not deleted. Try again.")


