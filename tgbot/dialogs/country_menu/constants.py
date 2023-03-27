from enum import Enum


class CountryMenu(str, Enum):
    COUNTRIES = "cm00"
    COUNTRIES_SG = "cm01"
    DELETE_COUNTRY_BUTTON = "cm02"
    ADD_COUNTRY_BUTTON = "cm03"

    def __str__(self) -> str:
        return str.__str__(self)
