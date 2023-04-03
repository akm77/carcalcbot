from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Jinja
from sqlalchemy.ext.asyncio import async_sessionmaker

from tgbot.config import Settings
from tgbot.models.db_commands import get_last_pairs, get_customs_clearance_fee, get_disposal_fee, get_excise_duty_fee, \
    get_duty_private_car_new, get_duty_private_car_aged, get_duty_entity_car, get_commission_fee, \
    get_other_russia_expenses_fee, get_japan_auction_fee, get_freight_rate, get_country_specific_expense
from tgbot.utils.decimals import value_to_decimal, format_decimal


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
                        data: dict) -> Optional[DualCurrencyValue]:
    sell_price = data.get("sell_price")
    sell_currency_code = data.get("sell_currency_code")

    if sell_currency_code == config.quote_currency:
        price = await convert_to_base_currency(session=db_session,
                                               base_currency=config.duty_base,
                                               quote_currency=config.quote_currency,
                                               quote_currency_value=value_to_decimal(sell_price))
    elif sell_currency_code == config.duty_base:
        price = await convert_to_quote_currency(session=db_session,
                                                base_currency=sell_currency_code,
                                                quote_currency=config.quote_currency,
                                                base_currency_value=value_to_decimal(sell_price))
    else:
        _price = await convert_to_quote_currency(session=db_session,
                                                 base_currency=sell_currency_code,
                                                 quote_currency=config.quote_currency,
                                                 base_currency_value=value_to_decimal(sell_price))
        price = await convert_to_base_currency(session=db_session,
                                               base_currency=config.duty_base,
                                               quote_currency=config.quote_currency,
                                               quote_currency_value=_price.quote_currency_value)
    return price


async def get_customs_clearance_cost(config: Settings,
                                     db_session: async_sessionmaker,
                                     price_rub: Decimal) -> Optional[DualCurrencyValue]:
    customs_clearance_fee = await get_customs_clearance_fee(session=db_session,
                                                            price=round(price_rub))
    return await convert_to_base_currency(session=db_session,
                                          base_currency=config.duty_base,
                                          quote_currency=config.quote_currency,
                                          quote_currency_value=customs_clearance_fee)


async def get_disposal_cost(config: Settings, db_session: async_sessionmaker,
                            data: dict) -> Optional[DualCurrencyValue]:
    if data.get("freight_type") == "indirect":
        return
    multiplier = await get_disposal_fee(session=db_session,
                                        buyer_type=data.get("buyer_type_code"),
                                        car_age=data.get("car_age_code"),
                                        engine_volume=data.get("engine_volume"))
    disposal_cost = value_to_decimal(config.disposal_fee * multiplier, decimal_places=2)
    return await convert_to_base_currency(session=db_session,
                                          base_currency=config.duty_base,
                                          quote_currency=config.quote_currency,
                                          quote_currency_value=disposal_cost)


async def get_excise(config: Settings, db_session: async_sessionmaker, data: dict) -> Optional[DualCurrencyValue]:
    if data.get("freight_type") == "indirect" or data.get("buyer_type_code") == "private":
        return
    engine_power = int(data.get("engine_power"))
    if data.get("uop_code") == "kw":
        engine_power = round(engine_power * value_to_decimal(1.35962, decimal_places=5))
    excise_duty_fee = await get_excise_duty_fee(session=db_session, engine_power=engine_power)
    excise_cost = excise_duty_fee * engine_power
    return await convert_to_base_currency(session=db_session,
                                          base_currency=config.duty_base,
                                          quote_currency=config.quote_currency,
                                          quote_currency_value=excise_cost)


async def get_customs_duty(db_session: async_sessionmaker, config: Settings, data: dict,
                           price_eur: Decimal) -> Optional[DualCurrencyValue]:
    car_age = data.get("car_age_code")
    engine_volume = int(data.get("engine_volume"))
    freight_type = data.get("freight_type")
    buyer_type_code = data.get("buyer_type_code")
    if freight_type == "indirect":
        return await convert_to_quote_currency(session=db_session,
                                               base_currency=config.duty_base,
                                               quote_currency=config.quote_currency,
                                               base_currency_value=price_eur * 30 / 100)
    if buyer_type_code == "private" and car_age == "age0":
        percent, check_value = await get_duty_private_car_new(session=db_session,
                                                              price=round(price_eur))
        customs_duty_percent = price_eur * percent / 100
        customs_duty_value = engine_volume * check_value
        customs_duty_fee = customs_duty_value if customs_duty_percent <= customs_duty_value else customs_duty_percent

    elif buyer_type_code == "private" and car_age != "age0":
        value = await get_duty_private_car_aged(session=db_session,
                                                car_age=car_age,
                                                engine_volume=engine_volume)
        customs_duty_fee = engine_volume * value
    else:
        engine_volume = int(data.get("engine_volume"))
        percent, check_value = await get_duty_entity_car(session=db_session,
                                                         fuel_type=data.get("fuel_code"),
                                                         car_age=data.get("car_age_code"),
                                                         engine_volume=engine_volume)
        customs_duty_percent = price_eur * percent / 100
        customs_duty_value = engine_volume * check_value
        customs_duty_fee = customs_duty_value if customs_duty_percent <= customs_duty_value else customs_duty_percent

    return await convert_to_quote_currency(session=db_session,
                                           base_currency=config.duty_base,
                                           quote_currency=config.quote_currency,
                                           base_currency_value=customs_duty_fee)


async def get_freight_cost(config: Settings, db_session: async_sessionmaker, data: dict) -> Optional[DualCurrencyValue]:
    country_code = data.get("country_code")
    freight_type = data.get("freight_type")
    freight_cost = await get_freight_rate(session=db_session, country_code=country_code, freight_type=freight_type)
    return await convert_to_quote_currency(session=db_session,
                                           base_currency=config.freight_base,
                                           quote_currency=config.quote_currency,
                                           base_currency_value=freight_cost)


async def get_non_customs_costs(config: Settings,
                                db_session: async_sessionmaker,
                                price_rub: Decimal) -> Optional[tuple]:
    commission = await get_commission_fee(session=db_session, price_rub=round(price_rub))
    gps = await get_other_russia_expenses_fee(session=db_session, code="gps")
    feed = await get_other_russia_expenses_fee(session=db_session, code="lab")
    return commission, gps, feed


async def get_japan_auction_cost(config: Settings,
                                 db_session: async_sessionmaker,
                                 price: DualCurrencyValue) -> Optional[DualCurrencyValue]:
    if price.base_currency == "JPY":
        price_jpy = price.base_currency_value
    else:
        _price = await convert_to_base_currency(session=db_session,
                                                base_currency="JPY",
                                                quote_currency=config.quote_currency,
                                                quote_currency_value=price.quote_currency_value)
        price_jpy = _price.base_currency_value
    fee = await get_japan_auction_fee(session=db_session, price_jpy=round(price_jpy))
    return await convert_to_quote_currency(session=db_session,
                                           base_currency="JPY",
                                           quote_currency=config.quote_currency,
                                           base_currency_value=fee)


async def get_country_specific_costs(config: Settings, db_session: async_sessionmaker, data: dict):
    country_code = data.get("country_code")
    freight_type = data.get("freight_type")

    deal_service_fee = await get_country_specific_expense(session=db_session,
                                                          country_code=country_code,
                                                          service_code="deal_service")
    delivery_service_fee = await get_country_specific_expense(session=db_session,
                                                              country_code=country_code,
                                                              service_code="delivery_service")
    broker_service_fee = await get_country_specific_expense(session=db_session,
                                                            country_code=country_code,
                                                            service_code="broker_service"
                                                            ) if freight_type == "indirect" else None
    logistic_service_fee = await get_country_specific_expense(session=db_session,
                                                              country_code=country_code,
                                                              service_code="logistic_service"
                                                              ) if freight_type == "indirect" else None
    return (await convert_to_quote_currency(session=db_session,
                                            base_currency=config.freight_base,
                                            quote_currency=config.quote_currency,
                                            base_currency_value=value_to_decimal(deal_service_fee)
                                            ) if deal_service_fee else None,
            await convert_to_quote_currency(session=db_session,
                                            base_currency=config.freight_base,
                                            quote_currency=config.quote_currency,
                                            base_currency_value=value_to_decimal(delivery_service_fee)
                                            ) if delivery_service_fee else None,
            await convert_to_quote_currency(session=db_session,
                                            base_currency=config.freight_base,
                                            quote_currency=config.quote_currency,
                                            base_currency_value=value_to_decimal(
                                                broker_service_fee)) if freight_type == "indirect" else None,
            await convert_to_quote_currency(session=db_session,
                                            base_currency=config.freight_base,
                                            quote_currency=config.quote_currency,
                                            base_currency_value=value_to_decimal(
                                                logistic_service_fee)) if freight_type == "indirect" else None
            )


def formatvalue(value: Decimal) -> str:
    return format_decimal(value, pre=2)


def get_message_text() -> str:
    minus_delimiter = f"<pre>{'-' * 30}</pre>\n"
    equal_delimiter = f"<pre>{'=' * 30}</pre>\n"
    header = minus_delimiter + "<i>Расчет стоимости\n</i>"

    customs_costs = """Цена: <b>{{price|formatvalue}}</b> {{currency}}
Таможенный сбор: <b>{{customs_clearance_cost|formatvalue}}</b> {{currency}}
{% if freight_type == "direct" %}
Утилизационный сбор: <b>{{disposal_cost|formatvalue}}</b> {{currency}}
{% endif %}
{% if buyer_type_code == "entity" and freight_type == "direct" %}
Акциз: <b>{{excise_cost|formatvalue}}</b> {{currency}}
Пошлина: <b>{{customs_duty|formatvalue}}</b> {{currency}} 
НДС: <b>{{vat|formatvalue}} {{currency}}</b>
{% endif %}
""" + equal_delimiter
    customs_total = "Итого: <b>{{customs_total|formatvalue}}</b> {{currency}}\n" + minus_delimiter

    non_customs_costs = """<i>Логистика, сертификация\nи сопровождение сделки</i>
{% if japan_auction_cost %}
Аукцион сбор/ 
Доставка до порта/ 
Комиссия брокера: <b>{{japan_auction_cost|formatvalue}}</b> {{currency}} 
{% endif %}
Фрахт (в том числе портовые сборы, 
погрузо/разгрузочные услуги): <b>{{freight_cost|formatvalue}}</b> {{currency}} 
{% if deal_service_fee %}
Выезд/осмотр/проверка/принятие денег: <b>{{deal_service_fee|formatvalue}}</b> {{currency}}
{% endif %}
{% if delivery_service_fee %}
Доставка до порта: <b>{{delivery_service_fee|formatvalue}}</b> {{currency}}
{% endif %}
{% if broker_service_fee %}
Услуга брокера: <b>{{broker_service_fee|formatvalue}}</b> {{currency}}
{% endif %}
{% if logistic_service_fee %}
Логистика до России: <b>{{logistic_service_fee|formatvalue}}</b> {{currency}}
{% endif %}
СВХ, СБКТС: <b>{{feed|formatvalue}}</b> {{currency}} 
Оборудование Эра-Глонасс: <b>{{gps|formatvalue}}</b> {{currency}} 
Комиссия: <b>{{commission|formatvalue}}</b> {{currency}}
""" + equal_delimiter
    grand_total = "<b>ВСЕГО: {{grand_total|formatvalue}}</b> {{currency}}"
    return header + customs_costs + customs_total + non_customs_costs + grand_total


async def cost_calculation(config: Settings, db_session: async_sessionmaker,
                           data: dict, manager: DialogManager) -> Optional[str]:
    buyer_type_code = data.get("buyer_type_code")
    country_code = data.get("country_code")
    freight_type = data.get("freight_type")  # direct indirect
    calculation_values = {"currency": config.quote_currency,
                          "buyer_type_code": buyer_type_code,
                          "country_code": country_code,
                          "freight_type": freight_type}

    price = await get_car_price(config=config, db_session=db_session, data=data)
    customs_clearance_cost = await get_customs_clearance_cost(config=config, db_session=db_session,
                                                              price_rub=price.quote_currency_value)
    disposal_cost = await get_disposal_cost(config=config, db_session=db_session, data=data)
    excise_cost = await get_excise(config=config,
                                   db_session=db_session,
                                   data=data)
    customs_duty = await get_customs_duty(db_session=db_session, config=config, data=data,
                                          price_eur=price.base_currency_value)
    vat = sum([price.quote_currency_value if price else 0,
               excise_cost.quote_currency_value if excise_cost else 0,
               customs_duty.quote_currency_value if customs_duty else 0]
              ) * 20 / 100 if buyer_type_code == "entity" else 0
    customs_total = sum([price.quote_currency_value if price else 0,
                         customs_clearance_cost.quote_currency_value if customs_clearance_cost else 0,
                         disposal_cost.quote_currency_value if disposal_cost else 0,
                         excise_cost.quote_currency_value if excise_cost else 0,
                         customs_duty.quote_currency_value if customs_duty else 0,
                         vat])

    japan_auction_cost = await get_japan_auction_cost(config=config,
                                                      db_session=db_session,
                                                      price=price) if country_code == "JP" else None
    freight_cost = await get_freight_cost(config=config, db_session=db_session, data=data)
    commission, gps, feed = await get_non_customs_costs(config=config,
                                                        db_session=db_session,
                                                        price_rub=price.quote_currency_value)
    deal_service_fee, delivery_service_fee, broker_service_fee, logistic_service_fee = await get_country_specific_costs(
        config=config, db_session=db_session, data=data)
    grand_total = sum([customs_total,
                       japan_auction_cost.quote_currency_value if japan_auction_cost else 0,
                       freight_cost.quote_currency_value if freight_cost else 0,
                       commission, gps, feed,
                       deal_service_fee.quote_currency_value if deal_service_fee else 0,
                       delivery_service_fee.quote_currency_value if delivery_service_fee else 0,
                       broker_service_fee.quote_currency_value if broker_service_fee else 0,
                       logistic_service_fee.quote_currency_value if logistic_service_fee else 0])
    calculation_values.update(price=price.quote_currency_value,
                              customs_clearance_cost=customs_clearance_cost.quote_currency_value,
                              disposal_cost=disposal_cost.quote_currency_value if disposal_cost else None,
                              customs_duty=customs_duty.quote_currency_value,
                              vat=vat,
                              customs_total=customs_total,
                              commission=commission,
                              gps=gps,
                              feed=feed,
                              japan_auction_cost=japan_auction_cost.quote_currency_value if japan_auction_cost else None,
                              freight_cost=freight_cost.quote_currency_value,
                              deal_service_fee=deal_service_fee.quote_currency_value if deal_service_fee else None,
                              delivery_service_fee=delivery_service_fee.quote_currency_value if delivery_service_fee else None,
                              broker_service_fee=broker_service_fee.quote_currency_value if broker_service_fee else None,
                              logistic_service_fee=logistic_service_fee.quote_currency_value if logistic_service_fee else None,
                              grand_total=grand_total)

    return await Jinja(get_message_text()).render_text(calculation_values, manager)
