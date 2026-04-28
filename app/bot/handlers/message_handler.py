from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bot.services.message_service import MessageService


@dataclass
class MessageHandler:
    service: MessageService

    def handle_update(self, update: dict[str, Any]) -> str:
        message = update.get("message", {})
        user = message.get("from", {})
        text = message.get("text", "")
        user_name = user.get("first_name", "user")
        return self.service.build_reply(text=text, user_name=user_name)
