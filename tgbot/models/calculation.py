from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import String, ForeignKey, text, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from tgbot.models.base import Base, AccountingInteger, TimestampMixin


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    language_code: Mapped[str] = mapped_column(nullable=True, server_default=text("ru_RU"))
    is_premium: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())
    role: Mapped[str] = mapped_column(String(length=100), server_default=text("user"))


class Currency(Base):
    __tablename__ = "currency"
    iso_code_char: Mapped[str] = mapped_column(String(3), primary_key=True)
    iso_code_num: Mapped[int] = mapped_column(index=True, unique=True)
    name_en: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    name_ru: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    nominal: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    symbol: Mapped[str] = mapped_column(String())
    countries: Mapped[List["CountryCurrency"]] = relationship()


class RuCentralBank(Base):
    __tablename__ = "currency_ru_cbr"
    iso_code_char: Mapped[str] = mapped_column(String(3), ForeignKey("currency.iso_code_char",
                                                                     ondelete="CASCADE",
                                                                     onupdate="CASCADE"),
                                               primary_key=True)
    cbr_currency_code: Mapped[str] = mapped_column(String(), nullable=False, unique=True)


class Country(Base):
    __tablename__ = "country"

    iso_code2: Mapped[str] = mapped_column(String(2), primary_key=True)
    is_code3: Mapped[str] = mapped_column(String(3), nullable=False, index=True, unique=True)
    short_name_en: Mapped[str] = mapped_column(String(), nullable=False, index=True, unique=True)
    short_name_ru: Mapped[str] = mapped_column(String(), nullable=False, index=True, unique=True)
    flag: Mapped[str] = mapped_column(String())


class CountryCurrency(Base):
    __tablename__ = "country_currency"

    country_iso_code2: Mapped[str] = mapped_column(String(2), ForeignKey("country.iso_code2",
                                                                         ondelete="CASCADE",
                                                                         onupdate="CASCADE"),
                                                   primary_key=True)
    currency_iso_code_char: Mapped[str] = mapped_column(String(3), ForeignKey("currency.iso_code_char",
                                                                              ondelete="CASCADE",
                                                                              onupdate="CASCADE"),
                                                        primary_key=True)
    country: Mapped["Country"] = relationship()


class CurrencyPair(TimestampMixin, Base):
    __tablename__ = "currency_pair"

    timestamp: Mapped[datetime.date] = mapped_column(Date(), primary_key=True)
    base_currency_code: Mapped[str] = mapped_column(ForeignKey("currency.iso_code_char",
                                                               ondelete="RESTRICT",
                                                               onupdate="CASCADE"),
                                                    primary_key=True)
    quote_currency_code: Mapped[str] = mapped_column(ForeignKey("currency.iso_code_char",
                                                                ondelete="RESTRICT",
                                                                onupdate="CASCADE"),
                                                     primary_key=True)
    nominal: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    value: Mapped[Decimal] = mapped_column(AccountingInteger, nullable=False, server_default=text("0"))
    base_currency: Mapped["Currency"] = relationship(foreign_keys=[base_currency_code])
    quote_currency: Mapped["Currency"] = relationship(foreign_keys=[quote_currency_code])
