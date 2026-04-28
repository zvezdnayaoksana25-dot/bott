from bot.services.message_service import MessageService

service = MessageService()


def test_empty_message_handled() -> None:
    assert service.build_reply(text="   ", user_name="Ann") == "Ann, я не получил текст сообщения"


def test_help_command_handled() -> None:
    assert "доступные команды" in service.build_reply(text="/help", user_name="Ann")


def test_ping_handled() -> None:
    assert service.build_reply(text="Ping please", user_name="Ann") == "Ann, pong"
