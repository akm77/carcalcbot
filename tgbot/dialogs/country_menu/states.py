from aiogram.fsm.state import StatesGroup, State


class CountryMenuStates(StatesGroup):
    select_country = State()
    add_country = State()
    edit_country = State()


