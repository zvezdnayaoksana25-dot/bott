from __future__ import annotations

from bot.config import Settings
from bot.handlers.message_handler import MessageHandler
from bot.services.message_service import MessageService


def create_handler() -> MessageHandler:
    _ = Settings.from_env()
    return MessageHandler(service=MessageService())
