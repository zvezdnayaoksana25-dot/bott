from __future__ import annotations

from dataclasses import dataclass

from bot.services.formatter import format_reply


@dataclass
class MessageService:
    """Critical business logic for message decisioning and response formatting."""

    def build_reply(self, *, text: str, user_name: str) -> str:
        normalized = text.strip().lower()
        if not normalized:
            return format_reply(user_name=user_name, body="я не получил текст сообщения")
        if normalized.startswith("/help"):
            return format_reply(
                user_name=user_name,
                body="доступные команды: /help, /ping, /remember",
            )
        if "ping" in normalized:
            return format_reply(user_name=user_name, body="pong")
        return format_reply(user_name=user_name, body=f"принято: {text.strip()}")
