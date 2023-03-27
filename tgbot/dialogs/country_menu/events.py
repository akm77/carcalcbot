import flag
from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput

from .import states
# from ...models.db_commands import upsert_country, get_countries_from_db


async def on_enter_country_code(message: Message,
                                message_input: MessageInput,
                                manager: DialogManager):
    db_session = manager.middleware_data.get("db_session")
    country = None
    countries = await get_countries_from_db(session=db_session)
    for country in countries:
        flag_ = flag.flag(country.iso2_code)
        await upsert_country(session=db_session, values={"iso3_code": country.iso3_code,
                                                         "iso2_code": country.iso2_code,
                                                         "name_short": country.name_short,
                                                         "name_official": country.name_official,
                                                         "flag": flag_})
    # if len(message.text) >= 3:
    #     country = countries.get(alpha_3=message.text[0:3])
    # elif len(message.text) == 2:
    #     country = countries.get(alpha_2=message.text[0:3])
    # if not country:
    #     await message.answer("Неверно указан код страны")
    #     return
    # await create_country(session=db_session, values=country)
    await manager.switch_to(states.CountryMenuStates.select_country)
