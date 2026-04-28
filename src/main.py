from __future__ import annotations

import asyncio
import logging
import signal

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from clients.groq_client import GroqClient
from config.logging import setup_logging
from config.settings import load_settings
from handlers.telegram_handlers import start_handler, text_handler
from services.chat_service import ChatService
from services.health_server import HealthServer

logger = logging.getLogger(__name__)


async def run() -> None:
    settings = load_settings()
    setup_logging(settings.log_level, settings.log_format)

    groq_client = GroqClient(
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        model=settings.groq_model,
        timeout_seconds=settings.request_timeout_seconds,
        retries=settings.request_retries,
        backoff_seconds=settings.request_backoff_seconds,
    )
    chat_service = ChatService(groq_client)
    health_server = HealthServer(settings.health_host, settings.health_port)

    app = Application.builder().token(settings.bot_token).build()
    app.bot_data["chat_service"] = chat_service
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _request_stop(sig_name: str) -> None:
        logger.info("Received shutdown signal", extra={"signal": sig_name})
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _request_stop, sig.name)

    await health_server.start()
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    logger.info("Bot started")

    try:
        await stop_event.wait()
    finally:
        logger.info("Shutting down bot")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        await health_server.stop()
        await groq_client.aclose()


if __name__ == "__main__":
    asyncio.run(run())
