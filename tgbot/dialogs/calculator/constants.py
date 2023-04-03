from enum import Enum


class CalculatorForm(str, Enum):
    SELECT_COUNTRY = "cf01"
    SELECT_SERVICE = "cf02"
    ENTER_VOLUME = "cf03"
    ENTER_PRICE = "cf04"
    ENTER_POWER = "cf05"
    SELECT_CAR_AGE = "cf06"
    SELECT_BUYER_TYPE = "cf07"
    SELECT_SELL_CURRENCY = "cf08"
    SELECT_FUEL_TYPE = "cf09"
    SELECT_UNIT_OF_POWER = "cf10"
    CALC_COSTS = "cf11"
    SELECT_FREIGHT_TYPE = "cf12"

    def __str__(self) -> str:
        return str.__str__(self)
