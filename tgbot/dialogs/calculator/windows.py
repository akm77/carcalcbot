from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format

from . import states, getters, keyboards

CALC_FORM = ("Поиск для: {started_by}\n"
             "{required_fields_text}\n"
             "<pre>------------------------------</pre>\n"
             "Страна: <b>{country_name}</b>\n"
             "Цена: <b>{sell_price}</b> {sell_currency} {sell_price_quote_currency}\n"
             "Возраст:  <b>{car_age}</b>\n"
             "Объем двигателя: <b>{engine_volume}</b> см3\n"
             "{engine_detail}"
             "Получатель: <b>{buyer_type_name}</b>\n"
             "{cost_calculation_text}")


def calculator_window():
    return Window(Format(CALC_FORM),
                  keyboards.select_country_kbd(),
                  keyboards.select_car_age_kbd(),
                  keyboards.select_sell_currency_price(),
                  keyboards.enter_engine_data(),
                  keyboards.select_buyer_type_kbd(),
                  keyboards.calc_final_action_kbd(),
                  state=states.CalculatorStates.enter_data,
                  getter=getters.calculator_form)


def calculator_input_window(text: str, handler=None, state=None, getter=None):
    return Window(
        Format(text),
        MessageInput(handler,
                     content_types=[ContentType.TEXT]),
        state=state,
        getter=getter
    )
