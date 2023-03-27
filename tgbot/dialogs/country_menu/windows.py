from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Row, SwitchTo, Back, Button
from aiogram_dialog.widgets.text import Const, Format

from . import states, getters, constants, keyboards, onclick, events


def country_list_window():
    return Window(Format("{started_by}\nСтраны"),
                  keyboards.countries_kbd(on_click=onclick.on_select_country),
                  Row(
                      Cancel(Const("<<")),
                      SwitchTo(Const("+"),
                               id=constants.CountryMenu.ADD_COUNTRY_BUTTON,
                               state=states.CountryMenuStates.add_country,
                               when="False")
                  ),
                  state=states.CountryMenuStates.select_country,
                  getter=getters.get_country_list)


def country_window():
    return Window(Format("{started_by}\nСтрана\n"
                         "Код ISO 3: {iso3_code}\n"
                         "Код ISO 2: {iso2_code}\n"
                         "Название: {name_short}\n"
                         "Официальное название: {name_official}\n"
                         "Флаг: {flag}"),
                  Row(
                      Back(Const("<<")),
                      Button(Const("❌ Удалить ‼️"),
                             id=constants.CountryMenu.DELETE_COUNTRY_BUTTON,
                             on_click=onclick.on_click_delete_country),
                  ),
                  state=states.CountryMenuStates.edit_country,
                  getter=getters.get_country)


def add_country_window():
    return Window(
        Format("{started_by}\n"
               "👇 Введите ISO 2 или ISO 3 код страны 👇"),
        MessageInput(events.on_enter_country_code,
                     content_types=[ContentType.TEXT]),
        state=states.CountryMenuStates.add_country,
        getter=getters.get_country
    )
