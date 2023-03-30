from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from sqlalchemy.ext.asyncio import async_sessionmaker

from tgbot.config import Settings
from tgbot.models.db_commands import get_last_pairs, get_customs_clearance_fee, get_disposal_fee, get_excise_duty_fee, \
    get_duty_private_car_new, get_duty_private_car_aged, get_duty_entity_car
from tgbot.utils.decimals import value_to_decimal


@dataclass
class DualCurrencyValue:
    base_currency: str
    base_currency_value: Decimal
    quote_currency: str
    quote_currency_value: Decimal
    nominal: int
    rate: Decimal
    rate_date: datetime.date


async def convert_to_quote_currency(session: async_sessionmaker,
                                    base_currency: str,
                                    quote_currency: str,
                                    base_currency_value: Decimal) -> Optional[DualCurrencyValue]:
    last_pairs = await get_last_pairs(session=session,
                                      base_currencies=[base_currency],
                                      quote_currency=quote_currency)
    if not last_pairs:
        raise ValueError(f"Pair {base_currency}/{quote_currency} not found")

    nominal = last_pairs[0].nominal
    rate = last_pairs[0].value
    rate_date = last_pairs[0].timestamp

    return DualCurrencyValue(base_currency=base_currency,
                             base_currency_value=base_currency_value,
                             quote_currency=quote_currency,
                             quote_currency_value=value_to_decimal(base_currency_value / Decimal(nominal) * rate,
                                                                   decimal_places=2),
                             nominal=nominal,
                             rate=rate,
                             rate_date=rate_date)


async def convert_to_base_currency(session: async_sessionmaker,
                                   base_currency: str,
                                   quote_currency: str,
                                   quote_currency_value: Decimal) -> Optional[DualCurrencyValue]:
    last_pairs = await get_last_pairs(session=session,
                                      base_currencies=[base_currency],
                                      quote_currency=quote_currency)
    if not last_pairs:
        raise ValueError(f"Pair {base_currency}/{quote_currency} not found")

    nominal = last_pairs[0].nominal
    rate = last_pairs[0].value
    rate_date = last_pairs[0].timestamp

    return DualCurrencyValue(base_currency=base_currency,
                             base_currency_value=value_to_decimal(quote_currency_value / rate * nominal,
                                                                  decimal_places=2),
                             quote_currency=quote_currency,
                             quote_currency_value=quote_currency_value,
                             nominal=nominal,
                             rate=rate,
                             rate_date=rate_date)


async def get_car_price(config: Settings,
                        db_session: async_sessionmaker,
                        data: dict) -> Optional[Dict[str, DualCurrencyValue]]:
    sell_price = data.get("sell_price")
    sell_currency_code = data.get("sell_currency_code")

    if sell_currency_code == config.quote_currency:
        price = {"USD": await convert_to_base_currency(session=db_session,
                                                       base_currency="USD",
                                                       quote_currency=config.quote_currency,
                                                       quote_currency_value=value_to_decimal(sell_price,
                                                                                             decimal_places=2)),
                 "EUR": await convert_to_base_currency(session=db_session,
                                                       base_currency="EUR",
                                                       quote_currency=config.quote_currency,
                                                       quote_currency_value=value_to_decimal(sell_price,
                                                                                             decimal_places=2))
                 }
    elif sell_currency_code not in config.form_currencies:
        price_sell_currency = await convert_to_quote_currency(session=db_session,
                                                              base_currency=sell_currency_code,
                                                              quote_currency=config.quote_currency,
                                                              base_currency_value=sell_price)
        price = {sell_currency_code: price_sell_currency,
                 "USD": await convert_to_base_currency(session=db_session,
                                                       base_currency="USD",
                                                       quote_currency=config.quote_currency,
                                                       quote_currency_value=price_sell_currency.quote_currency_value),
                 "EUR": await convert_to_base_currency(session=db_session,
                                                       base_currency="EUR",
                                                       quote_currency=config.quote_currency,
                                                       quote_currency_value=price_sell_currency.quote_currency_value)

                 }
    elif sell_currency_code == "EUR":
        price_sell_currency = await convert_to_quote_currency(session=db_session,
                                                              base_currency=sell_currency_code,
                                                              quote_currency=config.quote_currency,
                                                              base_currency_value=sell_price)
        price = {sell_currency_code: price_sell_currency,
                 "USD": await convert_to_base_currency(session=db_session,
                                                       base_currency="USD",
                                                       quote_currency=config.quote_currency,
                                                       quote_currency_value=price_sell_currency.quote_currency_value)
                 }
    else:
        price_sell_currency = await convert_to_quote_currency(session=db_session,
                                                              base_currency=sell_currency_code,
                                                              quote_currency=config.quote_currency,
                                                              base_currency_value=sell_price)
        price = {sell_currency_code: price_sell_currency,
                 "EUR": await convert_to_base_currency(session=db_session,
                                                       base_currency="EUR",
                                                       quote_currency=config.quote_currency,
                                                       quote_currency_value=price_sell_currency.quote_currency_value)
                 }
    return price


async def get_customs_clearance_cost(config: Settings,
                                     db_session: async_sessionmaker,
                                     price: Decimal) -> Optional[Dict[str, DualCurrencyValue]]:
    customs_clearance_fee = await get_customs_clearance_fee(session=db_session,
                                                            price=round(price))
    return {"USD": await convert_to_base_currency(session=db_session,
                                                  base_currency="USD",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=customs_clearance_fee),
            "EUR": await convert_to_base_currency(session=db_session,
                                                  base_currency="EUR",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=customs_clearance_fee)}


async def get_disposal_cost(config: Settings, db_session: async_sessionmaker,
                            data: dict) -> Optional[Dict[str, DualCurrencyValue]]:
    multiplier = await get_disposal_fee(session=db_session,
                                        buyer_type=data.get("buyer_type_code"),
                                        car_age=data.get("car_age_code"),
                                        engine_volume=data.get("engine_volume"))
    disposal_cost = value_to_decimal(config.disposal_fee * multiplier, decimal_places=2)
    return {"USD": await convert_to_base_currency(session=db_session,
                                                  base_currency="USD",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=disposal_cost),
            "EUR": await convert_to_base_currency(session=db_session,
                                                  base_currency="EUR",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=disposal_cost)}


async def get_excise(config: Settings, db_session: async_sessionmaker, data: dict):
    engine_power = int(data.get("engine_power"))
    if data.get("uop_code") == "kw":
        engine_power = round(engine_power * value_to_decimal(1.35962, decimal_places=5))
    excise_duty_fee = await get_excise_duty_fee(session=db_session, engine_power=engine_power)
    excise_cost = excise_duty_fee * engine_power
    return {"USD": await convert_to_base_currency(session=db_session,
                                                  base_currency="USD",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=excise_cost),
            "EUR": await convert_to_base_currency(session=db_session,
                                                  base_currency="EUR",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=excise_cost)}


async def get_customs_duty_private_car(db_session: async_sessionmaker, config: Settings, data: dict, price: Decimal):
    car_age = data.get("car_age_code")
    engine_volume = int(data.get("engine_volume"))
    if car_age == "age0":
        percent, check_value = await get_duty_private_car_new(session=db_session,
                                                              price=round(price))
        customs_duty_percent = price * percent / 100
        customs_duty_value = engine_volume * check_value
        customs_duty_fee = customs_duty_value if customs_duty_percent <= customs_duty_value else customs_duty_percent

    else:
        value = await get_duty_private_car_aged(session=db_session,
                                                car_age=car_age,
                                                engine_volume=engine_volume)
        customs_duty_fee = engine_volume * value
    customs_duty_in_duty_base = await convert_to_quote_currency(session=db_session,
                                                                base_currency=config.duty_base,
                                                                quote_currency=config.quote_currency,
                                                                base_currency_value=customs_duty_fee)
    return {config.duty_base: customs_duty_in_duty_base,
            "USD": await convert_to_base_currency(session=db_session,
                                                  base_currency="USD",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=customs_duty_in_duty_base.quote_currency_value)
            }


async def get_customs_duty_entity_car(db_session: async_sessionmaker, config: Settings, data: dict, price: Decimal):
    engine_volume = int(data.get("engine_volume"))
    percent, check_value = await get_duty_entity_car(session=db_session,
                                                     fuel_type=data.get("fuel_code"),
                                                     car_age=data.get("car_age_code"),
                                                     engine_volume=engine_volume)
    customs_duty_percent = price * percent / 100
    customs_duty_value = engine_volume * check_value
    customs_duty_fee = customs_duty_value if customs_duty_percent <= customs_duty_value else customs_duty_percent
    customs_duty_in_duty_base = await convert_to_quote_currency(session=db_session,
                                                                base_currency=config.duty_base,
                                                                quote_currency=config.quote_currency,
                                                                base_currency_value=customs_duty_fee)
    return {config.duty_base: customs_duty_in_duty_base,
            "USD": await convert_to_base_currency(session=db_session,
                                                  base_currency="USD",
                                                  quote_currency=config.quote_currency,
                                                  quote_currency_value=customs_duty_in_duty_base.quote_currency_value)
            }


async def cost_calculation_for_private(config: Settings, db_session: async_sessionmaker, data: dict) -> Optional[tuple]:
    price = await get_car_price(config=config, db_session=db_session, data=data)
    customs_clearance_cost = await get_customs_clearance_cost(config=config,
                                                              db_session=db_session,
                                                              price=price.get("EUR").quote_currency_value)
    disposal_cost = await get_disposal_cost(config=config, db_session=db_session, data=data)
    customs_duty = await get_customs_duty_private_car(db_session=db_session, config=config, data=data,
                                                      price=price["EUR"].base_currency_value)
    return price, customs_clearance_cost, disposal_cost, customs_duty


async def cost_calculation_for_entity(config: Settings, db_session: async_sessionmaker, data: dict) -> Optional[tuple]:
    price = await get_car_price(config=config, db_session=db_session, data=data)
    customs_clearance_cost = await get_customs_clearance_cost(config=config,
                                                              db_session=db_session,
                                                              price=price.get("EUR").quote_currency_value)
    disposal_cost = await get_disposal_cost(config=config, db_session=db_session, data=data)
    excise_cost = await get_excise(config=config,
                                   db_session=db_session,
                                   data=data)
    customs_duty = await get_customs_duty_entity_car(db_session=db_session,
                                                     config=config,
                                                     data=data,
                                                     price=price.get("EUR").base_currency_value)
    return price, customs_clearance_cost, disposal_cost, excise_cost, customs_duty


async def cost_calculation(config: Settings, db_session: async_sessionmaker, data: dict) -> Optional[str]:
    buyer_type_code = data.get("buyer_type_code")

    if buyer_type_code == "private":
        price, customs_clearance_cost, disposal_cost, customs_duty = \
            await cost_calculation_for_private(config=config, db_session=db_session, data=data)
        message_text = f"""Цена: {price["EUR"].quote_currency_value} {price["EUR"].quote_currency}
Таможенный сбор: {customs_clearance_cost["EUR"].quote_currency_value} {customs_clearance_cost["EUR"].quote_currency}
Утилизационный сбор: {disposal_cost["EUR"].quote_currency_value} {disposal_cost["EUR"].quote_currency} 
Пошлина: {customs_duty["EUR"].quote_currency_value} {customs_duty["EUR"].quote_currency} 
{"="*40}
"""
    else:
        price, customs_clearance_cost, disposal_cost, excise_cost, customs_duty = \
            await cost_calculation_for_entity(config=config, db_session=db_session, data=data)
        vat = (price["EUR"].quote_currency_value +
               excise_cost["EUR"].quote_currency_value +
               customs_duty["EUR"].quote_currency_value) * config.vat / 100
        message_text = f"""Цена: {price["EUR"].quote_currency_value} {price["EUR"].quote_currency}
Таможенный сбор: {customs_clearance_cost["EUR"].quote_currency_value} {customs_clearance_cost["EUR"].quote_currency}
Утилизационный сбор: {disposal_cost["EUR"].quote_currency_value} {disposal_cost["EUR"].quote_currency} 
Акциз: {excise_cost["EUR"].quote_currency_value} {excise_cost["EUR"].quote_currency} 
НДС: {vat} {excise_cost["EUR"].quote_currency}
Пошлина: {customs_duty["EUR"].quote_currency_value} {customs_duty["EUR"].quote_currency} 
{"="*40}
"""
    return message_text

