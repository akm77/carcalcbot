from dataclasses import dataclass
from decimal import Decimal
from typing import Dict


@dataclass
class Country:
    code: str
    name: str
    flag: str


countries: Dict[str, Country] = {"JP": Country(code="JP", name="Япония", flag="🇯🇵"),
                                 "KR": Country(code="KR", name="Ю. Корея", flag="🇰🇷"),
                                 "AE": Country(code="AE", name="ОАЭ", flag="🇦🇪"),
                                 "RU": Country(code="RU", name="Россия", flag="🇷🇺"),
                                 "EU": Country(code="EU", name="Европейский союз", flag="🇪🇺"),
                                 "US": Country(code="US", name="США", flag="🇺🇸")}


@dataclass
class Currency:
    code: str
    name: str
    symbol: str
    country: str


currencies_by_code = {"aed": Currency(code="AED", name="Дирхам", symbol=".د.إ", country="AE"),
                      "jpy": Currency(code="JPY", name="Йена", symbol="¥", country="JP"),
                      "krw": Currency(code="KRW", name="Вон", symbol="₩", country="KR"),
                      "rur": Currency(code="RUB", name="Российский рубль", symbol="₽", country="RU"),
                      "usd": Currency(code="USD", name="Доллар США", symbol="＄", country="US"),
                      "eur": Currency(code="EUR", name="Евро", symbol="€", country="EU")}

currencies_by_country = {"AE": Currency(code="AED", name="Дирхам", symbol=".د.إ", country="AE"),
                         "JP": Currency(code="JPY", name="Йена", symbol="¥", country="JP"),
                         "KR": Currency(code="KRW", name="Вон", symbol="₩", country="KR"),
                         "RU": Currency(code="RUB", name="Российский рубль", symbol="₽", country="RU"),
                         "US": Currency(code="RUB", name="Доллар США", symbol="＄", country="US"),
                         "EU": Currency(code="EUR", name="Евро", symbol="€", country="EU")}


@dataclass
class CurrencyRate:
    base_currency: str
    quote_currency: str
    ratio: int
    rate: Decimal


currency_rates = {"AED": CurrencyRate(base_currency="AED", quote_currency="RUB", ratio=1, rate=Decimal("21.12")),
                  "JPY": CurrencyRate(base_currency="JPY", quote_currency="RUB", ratio=100, rate=Decimal("57.3902")),
                  "KRW": CurrencyRate(base_currency="KRW", quote_currency="RUB", ratio=100, rate=Decimal("5.92"))}

# age: age0
# price: 1 000
# currency: usd
# dtype: ben
# obyem: 1500
# pwr_val: 150
# pwr: ls
# hybrid1: 3
# hybrid2: b
# lico: ur

unit_of_power = {"ls": "л.с",
                 "kvt": "кВт"}
car_age = {"age0": "Меньше 3 лет",
           "age3": "От 3 до 5 лет",
           "age5": "От 5 до 7 лет",
           "age7": "Больше 7 лет"}

buyer_type = {"fiz": "Физическое лицо",
              "ur": "Юридическое лицо"}

fuel_type = {"ben": "Бензин",
             "dis": "Дизель"}
