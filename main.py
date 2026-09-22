# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""EG Craft — async entry point."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Optional

from settings import Settings, load

log = logging.getLogger("egcraft.main")


class Game:
    """Game orchestrator. Holds subsystem references."""

    def __init__(self, settings: Settings, headless: bool = False) -> None:
        self.settings = settings
        self.headless = headless
        self.window = None  # type: Optional[object]
        self.world = None
        self.player = None
        self.entities_manager = None
        self.ui = None
        self.screens = None
        self.sounds = None
        self.music = None
        self.daynight = None
        self.survival = None
        self.mode = "survival"
        self.state = "splash"
        self.frame_count = 0
        self.max_frames: Optional[int] = None
        self.touch = None
        self.save_slots: list[str] = []
        self.stats = {"play_time": 0.0, "blocks_broken": 0,
                      "blocks_placed": 0, "mobs_killed": 0,
                      "deaths": 0, "distance_walked": 0.0}
        self.version = "2.0.0-commercial"

    def init_window(self) -> None:
        if self.window is not None:
            return
        if self.headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        from engine.window import Window
        self.window = Window(self.settings)
        try:
            from engine.touch import TouchBridge
            self.touch = TouchBridge()
        except Exception as exc:  # noqa: BLE001
            log.warning("TouchBridge init failed: %r", exc)
            self.touch = None

    async def run(self) -> None:
        self.init_window()
        while True:
            self._tick_one()
            if self.window is not None and not self.window.running:
                break
            if self.max_frames is not None and self.frame_count >= self.max_frames:
                break
            await asyncio.sleep(0)

    def _tick_one(self) -> None:
        self.frame_count += 1
        if self.window is not None:
            self.window.pump()
            if self.touch is not None and self.touch.is_mobile:
                self.touch.apply_to_window(self.window)
                self.touch.reset()
            self.window.swap()


def make_settings() -> Settings:
    return load()


def setup_environment(headless: bool) -> None:
    if headless:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        os.environ.setdefault("SDL_OPENGL_FORWARD_COMPAT", "1")


async def _async_main(settings: Settings | None = None) -> int:
    active_settings = settings or make_settings()
    headless = os.environ.get("EGCRAFT_HEADLESS") == "1"
    setup_environment(headless)
    game = Game(active_settings, headless=headless)
    await game.run()
    return 0


def main(settings: Settings | None = None) -> int:
    """Synchronous wrapper that drives the async loop."""
    from game.logging_setup import get_logger
    get_logger()
    try:
        return asyncio.run(_async_main(settings))
    except KeyboardInterrupt:
        log.info("Interrupted by user")
        return 0


async def aio_main() -> int:  # pragma: no cover
    return await _async_main()


async def _vercel_asgi_app(scope, receive, send):  # type: ignore[no-untyped-def]
    if scope["type"] != "http":
        return
    await receive()
    body = (b"<!doctype html><html lang='ar' dir='rtl'><head>"
            b"<meta charset='utf-8'><title>EG Craft</title></head>"
            b"<body><h1>EG Craft</h1>"
            b"<p>EG Craft يعمل كتطبيق WebAssembly عبر pygbag.</p>"
            b"<p><a href='/'>العودة للعبة</a></p></body></html>")
    await send({"type": "http.response.start", "status": 200,
                "headers": [[b"content-type", b"text/html; charset=utf-8"],
                             [b"content-length", str(len(body)).encode("ascii")]]})
    await send({"type": "http.response.body", "body": body})


app = _vercel_asgi_app


if __name__ == "__main__":
    sys.exit(main())
