import operator

from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Row, Button, SwitchTo, Checkbox, Counter, Group
from aiogram_dialog.widgets.text import Format

from . import constants, states, events, onclick


def countries_kbd(on_click, on_page_changed=None):
    return ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id=constants.CountryMenu.COUNTRIES,
            item_id_getter=operator.itemgetter(1),
            items="items",
            on_click=on_click,
        ),
        id=constants.CountryMenu.COUNTRIES_SG,
        width=1, height=10,
        on_page_changed=on_page_changed,
        hide_on_single_page=True
    )


def delete_country_kbd():
    return Row(
        Button(Format("❌ Delete {country} ‼️️"),
               id=constants.CountryMenu.DELETE_COUNTRY_BUTTON,
               on_click=onclick.on_click_delete_country)
    )


def add_country_kbd():
    return Row(
        SwitchTo(Format("+"),
                 id=constants.CountryMenu.ADD_COUNTRY_BUTTON,
                 state=states.CountryMenuStates.add_country)
    )
