from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from tgbot.models.db_commands import upsert_user_from_middleware


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config, db_session, http_session, http_proxy) -> None:
        self.config = config
        self.db_session = db_session
        self.http_session = http_session
        self.http_proxy = http_proxy

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data["config"] = self.config
        data["db_session"] = self.db_session
        data["http_session"] = self.http_session
        data["http_proxy"] = self.http_proxy
        return await handler(event, data)


class UserDBMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        ...

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        db_session = data.get("db_session")
        user = data.get("event_from_user")
        if user:
            db_user = await upsert_user_from_middleware(session=db_session, user=user)
            data["user_role"] = db_user.role
        return await handler(event, data)
