from decimal import Decimal
from typing import Sequence, Dict, List, Any

from charset_normalizer.md import Optional
from sqlalchemy import Result, select, delete, func
from sqlalchemy.dialects.sqlite import insert, Insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from tgbot.models.costing_data import User as DBUser, RuCentralBank, CurrencyPair, Country, Currency, CountryCurrency, \
    CustomsClearanceFee, ExciseDuty, DisposalFee, DutyPrivateCarNew, DutyPrivateCarAged, DutyEntityCar
from aiogram.types import User


def get_upsert_user_query(values) -> Insert:
    insert_statement = insert(DBUser).values(values)
    update_statement = insert_statement.on_conflict_do_update(
        index_elements=["id"],
        set_=dict(is_bot=insert_statement.excluded.is_bot,
                  first_name=insert_statement.excluded.first_name,
                  last_name=insert_statement.excluded.last_name,
                  username=insert_statement.excluded.username,
                  language_code=insert_statement.excluded.language_code,
                  is_premium=insert_statement.excluded.is_premium)).returning(DBUser)
    return update_statement


async def upsert_user_from_middleware(session: async_sessionmaker, user: User) -> Optional[DBUser]:
    # id: Mapped[int] = mapped_colu-mn(primary_key=True)
    # is_bot: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())
    # first_name: Mapped[str] = mapped_column(nullable=False)
    # last_name: Mapped[str] = mapped_column(nullable=True)
    # username: Mapped[str] = mapped_column(nullable=True)
    # lang_code: Mapped[str] = mapped_column(nullable=True, server_default=text("ru_RU"))
    # is_premium: Mapped[bool] = mapped_column(Boolean, server_default=expression.false())
    # role: Mapped[str] = mapped_column(String(length=100), server_default=text("user"))
    async with session() as session:
        result: Result = await session.execute(get_upsert_user_query({"id": user.id,
                                                                      "is_bot": user.is_bot,
                                                                      "first_name": user.first_name,
                                                                      "last_name": user.last_name,
                                                                      "username": user.username,
                                                                      "language_code": user.language_code,
                                                                      "is_premium": user.is_premium if user.is_premium
                                                                      else False}))
        await session.commit()
        return result.scalars().one_or_none()


async def get_cbr_currency_codes(session: async_sessionmaker,
                                 codes: Optional[List[str]] = None) -> Optional[Sequence[RuCentralBank]]:
    select_statement = select(RuCentralBank)
    if codes:
        select_statement = select_statement.where(RuCentralBank.iso_code_char.in_(codes))

    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalars().all()


async def upsert_currency_pair(session: async_sessionmaker,
                               values: List[Dict[str, Any]]) -> Optional[Sequence[CurrencyPair]]:
    async with session() as session:
        result: Result = await session.execute(insert(CurrencyPair).values(values).on_conflict_do_nothing(
            index_elements=["timestamp", "base_currency_code", "quote_currency_code"]).returning(CurrencyPair))
        await session.commit()
    return result.scalars().all()


async def get_last_pairs(session: async_sessionmaker,
                         base_currencies: Optional[List[str]] = None,
                         quote_currency: Optional[str] = "RUB") -> Optional[Sequence[CurrencyPair]]:
    get_last_timestamp = select(func.max(CurrencyPair.timestamp).label("last_timestamp")).cte()
    select_statement = select(CurrencyPair)
    if base_currencies:
        select_statement = select_statement.where(CurrencyPair.timestamp == get_last_timestamp.c.last_timestamp,
                                                  CurrencyPair.quote_currency_code == quote_currency,
                                                  CurrencyPair.base_currency_code.in_(base_currencies))
    else:
        select_statement = select_statement.where(CurrencyPair.timestamp == get_last_timestamp.c.last_timestamp,
                                                  CurrencyPair.quote_currency_code == quote_currency)

    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalars().all()


async def get_countries(session: async_sessionmaker,
                        countries: Optional[List[str]] = None) -> Optional[Sequence[Country]]:
    select_statement = select(Country)
    if countries:
        select_statement = select_statement.where(Country.iso_code2.in_(countries))

    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalars().all()


async def get_currencies(session: async_sessionmaker,
                         currencies: Optional[List[str]] = None) -> Optional[Sequence[Currency]]:
    select_statement = select(Currency)
    if currencies:
        select_statement = select_statement.where(Currency.iso_code_char.in_(currencies))

    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalars().all()


async def get_country_currency(session: async_sessionmaker, country: str) -> Optional[CountryCurrency]:
    async with session() as session:
        result: Result = await session.execute(select(CountryCurrency).where(
            CountryCurrency.country_iso_code2 == country))
    return result.scalars().one_or_none()


async def get_customs_clearance_fee(session: async_sessionmaker, price: int) -> Optional[Decimal]:
    price_boundary = select(func.max(CustomsClearanceFee.price).label("boundary"))
    price_boundary = price_boundary.where(CustomsClearanceFee.price < price).cte("price_boundary")
    select_statement = select(CustomsClearanceFee.fee).where(CustomsClearanceFee.price == price_boundary.c.boundary)
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalar_one_or_none()


async def get_excise_duty_fee(session: async_sessionmaker, engine_power: int) -> Optional[Decimal]:
    power_boundary = select(func.max(ExciseDuty.engine_power).label("boundary"))
    power_boundary = power_boundary.where(ExciseDuty.engine_power < engine_power).cte("power_boundary")
    select_statement = select(ExciseDuty.fee).where(ExciseDuty.engine_power == power_boundary.c.boundary)
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalar_one_or_none()


async def get_disposal_fee(session: async_sessionmaker,
                           buyer_type: str,
                           car_age: str,
                           engine_volume: int) -> Optional[Decimal]:
    volume_boundary = select(func.max(DisposalFee.engine_volume).label("boundary"))
    volume_boundary = volume_boundary.where(DisposalFee.buyer_type == buyer_type,
                                            DisposalFee.car_age == car_age,
                                            DisposalFee.engine_volume < engine_volume).cte("volume_boundary")
    select_statement = select(DisposalFee.multiplier).where(DisposalFee.buyer_type == buyer_type,
                                                            DisposalFee.car_age == car_age,
                                                            DisposalFee.engine_volume == volume_boundary.c.boundary)
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalar_one_or_none()


async def get_duty_private_car_new(session: async_sessionmaker,
                                   price: int) -> Optional[Any]:
    price_boundary = select(func.max(DutyPrivateCarNew.price).label("boundary"))
    price_boundary = price_boundary.where(DutyPrivateCarNew.price < price).cte("price_boundary")
    select_statement = select(DutyPrivateCarNew.percent, DutyPrivateCarNew.check_value)
    select_statement = select_statement.where(DutyPrivateCarNew.price == price_boundary.c.boundary)
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.one_or_none()


async def get_duty_private_car_aged(session: async_sessionmaker,
                                    car_age: str,
                                    engine_volume: int) -> Optional[Decimal]:
    volume_boundary = select(func.max(DutyPrivateCarAged.engine_volume).label("boundary"))
    volume_boundary = volume_boundary.where(DutyPrivateCarAged.car_age == car_age,
                                            DutyPrivateCarAged.engine_volume < engine_volume).cte("volume_boundary")

    select_statement = select(DutyPrivateCarAged.value)
    select_statement = select_statement.where(DutyPrivateCarAged.car_age == car_age,
                                              DutyPrivateCarAged.engine_volume == volume_boundary.c.boundary)
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalar_one_or_none()


async def get_duty_entity_car(session: async_sessionmaker,
                              fuel_type: str,
                              car_age: str,
                              engine_volume: int) -> Optional[Any]:
    volume_boundary = select(func.max(DutyEntityCar.engine_volume).label("boundary"))
    volume_boundary = volume_boundary.where(DutyEntityCar.fuel_type == fuel_type,
                                            DutyEntityCar.car_age == car_age,
                                            DutyEntityCar.engine_volume < engine_volume).cte("volume_boundary")
    select_statement = select(DutyEntityCar.percent, DutyEntityCar.check_value)
    select_statement = select_statement.where(DutyEntityCar.fuel_type == fuel_type,
                                              DutyEntityCar.car_age == car_age,
                                              DutyEntityCar.engine_volume == volume_boundary.c.boundary)
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.one_or_none()
