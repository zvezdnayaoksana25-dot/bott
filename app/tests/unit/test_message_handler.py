from bot.handlers.message_handler import MessageHandler
from bot.services.message_service import MessageService


def test_message_handler_uses_service(sample_update: dict[str, object]) -> None:
    handler = MessageHandler(service=MessageService())
    reply = handler.handle_update(sample_update)
    assert reply == "Alex, pong"
