from __future__ import annotations

import logging
import sys
from logging.config import dictConfig

from pythonjsonlogger import jsonlogger


class _JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):  # type: ignore[no-untyped-def]
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("level", record.levelname)
        log_record.setdefault("logger", record.name)


def setup_logging(level: str = "INFO", fmt: str = "json") -> None:
    formatter = "json" if fmt == "json" else "plain"

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
            },
            "json": {
                "()": _JsonFormatter,
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": formatter,
            },
        },
        "root": {
            "handlers": ["stdout"],
            "level": level,
        },
    }

    dictConfig(config)


__all__ = ["setup_logging"]
