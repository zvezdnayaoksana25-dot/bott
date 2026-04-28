from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from aiohttp import web

logger = logging.getLogger(__name__)


class HealthServer:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._app = web.Application()
        self._app.add_routes([web.get("/health", self._health)])
        self._runner = web.AppRunner(self._app)
        self._site: web.TCPSite | None = None

    async def _health(self, _: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def start(self) -> None:
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()
        logger.info("Health endpoint is listening", extra={"host": self._host, "port": self._port})

    async def stop(self) -> None:
        with suppress(asyncio.CancelledError):
            if self._site:
                await self._site.stop()
            await self._runner.cleanup()
