from bot.services.formatter import format_reply


def test_format_reply_plain() -> None:
    assert format_reply(user_name="Alex", body="  hello  ") == "Alex, hello"


def test_format_reply_markdown() -> None:
    assert format_reply(user_name="Alex", body="world", use_markdown=True) == "*Alex*, world"
