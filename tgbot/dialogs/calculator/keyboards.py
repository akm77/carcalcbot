import operator

from aiogram_dialog.widgets.kbd import Row, Radio, Group, Button, SwitchTo, Cancel
from aiogram_dialog.widgets.text import Format, Const

from . import constants, events, states, onclick, whenable
from .whenable import is_legal_entity


def select_country_kbd():
    return Group(
        Radio(
            Format("✓ {item[0]}"),
            Format("  {item[0]}"),
            id=constants.CalculatorForm.SELECT_COUNTRY,
            item_id_getter=operator.itemgetter(1),
            on_state_changed=events.on_country_changed,
            items="countries",
        ),
        width=3
    )


def enter_engine_data():
    return Group(
        Row(
            SwitchTo(Const("✍️ Объём"),
                     id=constants.CalculatorForm.ENTER_VOLUME,
                     state=states.CalculatorStates.enter_volume),
            select_fuel_type_kbd()),
        Row(
            SwitchTo(Const("✍️ Мощность"),
                     id=constants.CalculatorForm.ENTER_POWER,
                     state=states.CalculatorStates.enter_power,
                     when=is_legal_entity),
            select_unit_of_power_kbd()
        )
    )


def select_fuel_type_kbd():
    return Radio(
        Format("✓ {item[0]}"),
        Format("  {item[0]}"),
        id=constants.CalculatorForm.SELECT_FUEL_TYPE,
        item_id_getter=operator.itemgetter(1),
        on_state_changed=events.on_fuel_type_changed,
        items="fuel_types",
        when=is_legal_entity
    )


def select_unit_of_power_kbd():
    return Radio(
        Format("✓ {item[0]}"),
        Format("  {item[0]}"),
        id=constants.CalculatorForm.SELECT_UNIT_OF_POWER,
        item_id_getter=operator.itemgetter(1),
        on_state_changed=events.on_uop_changed,
        items="units_of_power",
        when=is_legal_entity
    )


def select_sell_currency_price():
    return Group(SwitchTo(Const("✍️ Цена"),
                          id=constants.CalculatorForm.ENTER_PRICE,
                          state=states.CalculatorStates.enter_price),
                 Radio(
                     Format("✓ {item[0]}"),
                     Format("  {item[0]}"),
                     id=constants.CalculatorForm.SELECT_SELL_CURRENCY,
                     item_id_getter=operator.itemgetter(1),
                     on_state_changed=events.on_sell_currency_changed,
                     items="sell_currencies",
                 ),
                 width=3

                 )


def select_car_age_kbd():
    return Group(
        Radio(
            Format("✓ {item[0]}"),
            Format("  {item[0]}"),
            id=constants.CalculatorForm.SELECT_CAR_AGE,
            item_id_getter=operator.itemgetter(1),
            on_state_changed=events.on_car_age_changed,
            items="car_ages",
        ),
        width=2
    )


def select_buyer_type_kbd():
    return Row(
        Radio(
            Format("✓ {item[0]}"),
            Format("  {item[0]}"),
            id=constants.CalculatorForm.SELECT_BUYER_TYPE,
            item_id_getter=operator.itemgetter(1),
            on_state_changed=events.on_buyer_type_changed,
            items="buyer_types",
        ),
        when=whenable.is_direct_freight
    )


def calc_final_action_kbd():
    return Row(
        Cancel(Const("<<"),
               id="__exit__"),
        Button(Const("🏁 Рассчитать 🚀"),
               id=constants.CalculatorForm.CALC_COSTS,
               on_click=onclick.on_click_calculate,
               when=whenable.check_required_fields)
    )


def select_freight_type_kbd():
    return Row(
        Radio(
            Format("✓ {item[0]}"),
            Format("  {item[0]}"),
            id=constants.CalculatorForm.SELECT_FREIGHT_TYPE,
            item_id_getter=operator.itemgetter(1),
            on_state_changed=events.on_freight_type_changed,
            items="freight_types"
        ),
        when=whenable.is_not_japan
    )
