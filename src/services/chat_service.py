from __future__ import annotations

import logging

from clients.groq_client import GroqClient, GroqClientError

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, groq_client: GroqClient) -> None:
        self._groq_client = groq_client

    async def generate_answer(self, text: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return "Пожалуйста, отправьте непустое сообщение."

        try:
            return await self._groq_client.generate_reply(cleaned)
        except GroqClientError as exc:
            logger.exception("Groq request failed")
            return "Сервис временно недоступен. Попробуйте чуть позже."
