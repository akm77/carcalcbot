from aiogram_dialog import DialogManager

from tgbot.models.fakle_repo import countries, fuel_type, car_age, buyer_type, currencies_by_code, unit_of_power
from . import constants


async def calculator_form(dialog_manager: DialogManager, **middleware_data):
    session = middleware_data.get('db_session')
    ctx = dialog_manager.current_context()
    db_countries = [(f"{country.flag} {country.name}", country.code) for country in countries.values() if
                    country.code in ("JP", "KR", "AE")]
    db_fuel_type = [(fuel, fuel_code) for fuel_code, fuel in fuel_type.items()]
    db_car_ages = [(age, id) for id, age in car_age.items()]
    db_buyer_types = [(buyer, id) for id, buyer in buyer_type.items()]
    db_sell_currencies = [(f"{sell_currency.code} {sell_currency.symbol}", id)
                          for id, sell_currency in currencies_by_code.items()
                          if id != "aed"]
    db_unit_of_power = [(unit, id) for id, unit in unit_of_power.items()]

    start_data = ctx.start_data
    dialog_data = ctx.dialog_data
    started_by = start_data.get("started_by") or "UNKNOWN"
    sell_price = dialog_data.get("sell_price") or 0
    engine_volume = dialog_data.get("engine_volume") or 0
    engine_power = dialog_data.get("engine_power") or 0

    country_code = dialog_data.get("country_code") or start_data.get("country_code")
    country_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_COUNTRY)
    await country_kbd.set_checked(item_id=country_code)
    country_name = countries.get(country_code)

    fuel_code = dialog_data.get("fuel_code") or start_data.get("fuel_code")
    select_fuel_type_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_FUEL_TYPE)
    await select_fuel_type_kbd.set_checked(item_id=fuel_code)
    fuel_name = fuel_type.get(fuel_code)

    sell_currency_code = dialog_data.get("sell_currency_code") or start_data.get("sell_currency_code")
    select_sell_currency_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_SELL_CURRENCY)
    await select_sell_currency_kbd.set_checked(item_id=sell_currency_code)
    sell_currency = currencies_by_code.get(sell_currency_code)
    if not sell_currency:
        await dialog_manager.done()

    car_age_code = dialog_data.get("car_age_code") or start_data.get("car_age_code")
    car_age_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_CAR_AGE)
    await car_age_kbd.set_checked(item_id=car_age_code)
    car_age_name = car_age.get(car_age_code)

    buyer_type_code = dialog_data.get("buyer_type_code") or start_data.get("buyer_type_code")
    select_buyer_type_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_BUYER_TYPE)
    await select_buyer_type_kbd.set_checked(item_id=buyer_type_code)
    buyer_type_name = buyer_type.get(buyer_type_code)

    uop_code = dialog_data.get("uop_code") or start_data.get("uop_code")
    select_unit_of_power_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_UNIT_OF_POWER)
    await select_unit_of_power_kbd.set_checked(item_id=uop_code)
    uop_name = unit_of_power.get(uop_code)

    required_fields_text = ("Обязательно заполнить <b>Цена закупки</b>, "
                            "<b>Объем двигателя</b>, <b>Мощность двигателя</b>"
                            if buyer_type_code == "ur" else "Обязательно заполнить <b>Цена закупки</b>, "
                                                            "<b>Объем двигателя</b>")
    engine_detail = (f"Тип топлива: <b>{fuel_name}</b>\n"
                      f"Мощность двигателя: <b>{engine_power}</b> {uop_name}\n") if buyer_type_code == "ur" else ""

    return {"started_by": started_by,
            "required_fields_text": required_fields_text,
            "engine_detail": engine_detail,
            "sell_currency": f"{sell_currency.symbol} ({sell_currency.code})",
            "sell_price": sell_price,
            "country_name": f"{country_name.flag} {country_name.name}",
            "fuel_name": fuel_name,
            "engine_volume": engine_volume,
            "engine_power": engine_power,
            "uop_name": uop_name,
            "car_age_name": car_age_name,
            "buyer_type_name": buyer_type_name,
            "sell_currencies": db_sell_currencies,
            "buyer_types": db_buyer_types,
            "car_ages": db_car_ages,
            "fuel_types": db_fuel_type,
            "countries": db_countries,
            "units_of_power": db_unit_of_power}
