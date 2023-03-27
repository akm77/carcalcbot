from aiogram_dialog import Dialog

from . import windows, events, states, getters


def calculator_dialogs():
    return [
        Dialog(
            windows.calculator_window(),
            windows.calculator_input_window(text="👇 Введите цену в {sell_currency} 👇",
                                            handler=events.on_enter_price,
                                            state=states.CalculatorStates.enter_price,
                                            getter=getters.calculator_form),
            windows.calculator_input_window(text="👇 Введите объем двигателя ({engine_volume}) см3 👇",
                                            handler=events.on_enter_volume,
                                            state=states.CalculatorStates.enter_volume,
                                            getter=getters.calculator_form),
            windows.calculator_input_window(text="👇 Введите мощность двигателя ({engine_power}) л.c. 👇",
                                            handler=events.on_enter_power,
                                            state=states.CalculatorStates.enter_power,
                                            getter=getters.calculator_form),
            on_start=None,
            on_process_result=None
        )
    ]
