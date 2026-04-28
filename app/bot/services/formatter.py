from __future__ import annotations


def format_reply(*, user_name: str, body: str, use_markdown: bool = False) -> str:
    clean_body = body.strip()
    if use_markdown:
        return f"*{user_name}*, {clean_body}"
    return f"{user_name}, {clean_body}"
