from aiogram.types import Message
from aiogram_dialog import DialogManager

# from tgbot.models.db_commands import get_countries_from_db, get_country_from_db


async def get_country_list(dialog_manager: DialogManager, **middleware_data):
    session = middleware_data.get('db_session')

    # started_by = dialog_manager.start_data.get("started_by") or "UNKNOWN"
    # countries = await get_countries_from_db(session=session)
    # items = [(f"{country.flag} {country.name_short}",
    #           country.iso3_code)
    #          for country in countries if countries]
    #
    # return {"started_by": started_by,
    #         "items": items}


async def get_country(dialog_manager: DialogManager, **middleware_data):
    session = middleware_data.get('db_session')
    ctx = dialog_manager.current_context()
    # iso3_code = ctx.dialog_data.get("iso3_code")
    # started_by = dialog_manager.start_data.get("started_by") or "UNKNOWN"
    # country = await get_country_from_db(session=session, iso3_code=iso3_code)
    #
    # return {"started_by": started_by,
    #         "iso3_code": country.iso3_code if country else "",
    #         "iso2_code": country.iso2_code if country else "",
    #         "name_short": country.name_short if country else "",
    #         "name_official": country.name_official if country else "",
    #         "flag": country.flag if country else ""}
