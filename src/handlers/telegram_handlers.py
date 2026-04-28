from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from services.chat_service import ChatService


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Отправьте вопрос, и я отвечу через Groq.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_service: ChatService = context.application.bot_data["chat_service"]
    message = update.message.text if update.message else ""
    answer = await chat_service.generate_answer(message)
    await update.message.reply_text(answer)
