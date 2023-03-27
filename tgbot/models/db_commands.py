from typing import Sequence, Dict, List, Any

from charset_normalizer.md import Optional
from sqlalchemy import Result, select, delete, func
from sqlalchemy.dialects.sqlite import insert, Insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from tgbot.models.calculation import User as DBUser, RuCentralBank, CurrencyPair
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
    # id: Mapped[int] = mapped_column(primary_key=True)
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


async def get_cbr_currency_codes(session: async_sessionmaker, codes: List[str]) -> Optional[Sequence[RuCentralBank]]:
    async with session() as session:
        result: Result = await session.execute(select(RuCentralBank).where(RuCentralBank.iso_code_char.in_(codes)))
    return result.scalars().all()


async def upsert_currency_pair(session: async_sessionmaker,
                               values: List[Dict[str, Any]]) -> Optional[Sequence[CurrencyPair]]:
    async with session() as session:
        result: Result = await session.execute(insert(CurrencyPair).values(values).on_conflict_do_nothing(
            index_elements=["timestamp", "base_currency_code", "quote_currency_code"]).returning(CurrencyPair))
        await session.commit()
    return result.scalars().all()


async def get_last_pairs(session: async_sessionmaker, base_currency: List[str]) -> Optional[Sequence[CurrencyPair]]:

    get_last_timestamp = select(func.max(CurrencyPair.timestamp).label("last_timestamp")).cte()
    select_statement = select(CurrencyPair).where(CurrencyPair.timestamp == get_last_timestamp.c.last_timestamp,
                                                  CurrencyPair.base_currency_code.in_(base_currency))
    async with session() as session:
        result: Result = await session.execute(select_statement)
    return result.scalars().all()
