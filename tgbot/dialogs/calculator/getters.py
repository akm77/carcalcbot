from copy import copy

from aiogram_dialog import DialogManager

from . import constants
from ...config import Settings
from ...models.db_commands import get_countries, get_currencies, get_country_currency, get_last_pairs
from ...utils.decimals import value_to_decimal


async def calculator_form(dialog_manager: DialogManager, **middleware_data):
    session = middleware_data.get('db_session')
    config: Settings = middleware_data.get("config")
    ctx = dialog_manager.current_context()
    start_data = ctx.start_data
    dialog_data = ctx.dialog_data

    started_by = start_data.get("started_by") or "UNKNOWN"
    sell_price = dialog_data.get("sell_price") or 0
    engine_volume = dialog_data.get("engine_volume") or 0
    engine_power = dialog_data.get("engine_power") or 0
    country_code = dialog_data.get("country_code") or start_data.get("country_code")
    fuel_code = dialog_data.get("fuel_code") or start_data.get("fuel_code")
    sell_currency_code = dialog_data.get("sell_currency_code") or start_data.get("sell_currency_code")
    car_age_code = dialog_data.get("car_age_code") or start_data.get("car_age_code")
    buyer_type_code = dialog_data.get("buyer_type_code") or start_data.get("buyer_type_code")
    uop_code = dialog_data.get("uop_code") or start_data.get("uop_code")

    last_pair = await get_last_pairs(session=session, base_currencies=[sell_currency_code])
    if last_pair:
        lp = last_pair[0]
        sell_price_quote_currency = (f"({round(value_to_decimal(sell_price) / lp.nominal * lp.value)} "
                                     f"{lp.quote_currency_code})")
    else:
        sell_price_quote_currency = ""

    db_countries = await get_countries(session, countries=config.form_countries)
    countries = [(f"{country.flag} {country.short_name_ru}", country.iso_code2) for country in db_countries]

    fuel_types = [(fuel, fuel_code) for fuel_code, fuel in config.fuel_types.items()]

    if buyer_type_code == "private":
        car_age_ranges = config.age_range_private
    else:
        car_age_ranges = config.age_range_entity
    car_ages = [(age, id) for id, age in (car_age_ranges.items())]

    buyer_types = [(buyer, id) for id, buyer in config.buyer_types.items()]
    units_of_power = [(unit, id) for id, unit in config.units_of_power.items()]

    db_country_currency = await get_country_currency(session, country=country_code)
    form_currencies = copy(config.form_currencies)
    if db_country_currency:
        form_currencies.append(db_country_currency.currency_iso_code_char)
    db_sell_currencies = await get_currencies(session, currencies=list(set(form_currencies)))

    sell_currencies = [(f"{sell_currency.iso_code_char}", sell_currency.iso_code_char)
                       for sell_currency in db_sell_currencies]

    country_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_COUNTRY)
    await country_kbd.set_checked(item_id=country_code)
    country_name = next((country[0] for country in countries if country[1] == country_code))

    select_fuel_type_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_FUEL_TYPE)
    await select_fuel_type_kbd.set_checked(item_id=fuel_code)
    fuel_name = config.fuel_types.get(fuel_code)

    select_sell_currency_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_SELL_CURRENCY)
    await select_sell_currency_kbd.set_checked(item_id=sell_currency_code)
    sell_currency = sell_currency_code
    # sell_currency = next((currency[0] for currency in sell_currencies if currency[1] == sell_currency_code))
    if not sell_currency:
        await dialog_manager.done()

    car_age_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_CAR_AGE)
    await car_age_kbd.set_checked(item_id=car_age_code)
    car_age = car_age_ranges.get(car_age_code)

    select_buyer_type_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_BUYER_TYPE)
    await select_buyer_type_kbd.set_checked(item_id=buyer_type_code)
    buyer_type_name = config.buyer_types.get(buyer_type_code)

    select_unit_of_power_kbd = dialog_manager.find(constants.CalculatorForm.SELECT_UNIT_OF_POWER)
    await select_unit_of_power_kbd.set_checked(item_id=uop_code)
    uop_name = config.units_of_power.get(uop_code)

    required_fields_text = ("Обязательно заполнить <b>Цена</b>, "
                            "<b>Объем двигателя</b>, <b>Мощность двигателя</b>"
                            if buyer_type_code == "entity" else "Обязательно заполнить <b>Цена</b>, "
                                                                "<b>Объем двигателя</b>")
    engine_detail = (f"Тип топлива: <b>{fuel_name}</b>\n"
                     f"Мощность двигателя: <b>{engine_power}</b> {uop_name}\n") if buyer_type_code == "entity" else ""

    return {"started_by": started_by,
            "required_fields_text": required_fields_text,
            "engine_detail": engine_detail,
            "sell_currency": f"{sell_currency}",
            "sell_price_quote_currency": sell_price_quote_currency,
            "sell_price": sell_price,
            "country_name": f"{country_name}",
            "fuel_name": fuel_name,
            "engine_volume": engine_volume,
            "engine_power": engine_power,
            "uop_name": uop_name,
            "car_age": car_age,
            "buyer_type_name": buyer_type_name,
            "sell_currencies": sell_currencies,
            "buyer_types": buyer_types,
            "car_ages": car_ages,
            "fuel_types": fuel_types,
            "countries": countries,
            "units_of_power": units_of_power}
