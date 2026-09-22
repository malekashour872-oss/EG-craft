# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Touch input bridge for the pygbag web build."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import pygame

log = logging.getLogger("egcraft.touch")


@dataclass
class TouchInputState:
    """Mirror of window.EGC.input on the JS side."""

    move_x: float = 0.0
    move_y: float = 0.0
    look_dx: float = 0.0
    look_dy: float = 0.0
    jump: bool = False
    sneak: bool = False
    fly_toggle: bool = False
    break_held: bool = False
    place_held: bool = False
    inv_toggle: bool = False
    hotbar_index: int = 0

    def reset_deltas(self) -> None:
        self.look_dx = 0.0
        self.look_dy = 0.0
        self.fly_toggle = False
        self.inv_toggle = False


class TouchBridge:
    """Bridge JS touch input to the pygame-compatible window state."""

    def __init__(self) -> None:
        self.is_mobile = self._detect_pygbag()
        self.state = TouchInputState()

    def _detect_pygbag(self) -> bool:
        try:
            import sys
            return ("emscripten" in sys.platform.lower()
                    or "pygbag" in sys.modules)
        except Exception:  # noqa: BLE001
            return False

    def _get_js_input(self) -> TouchInputState:
        if not self.is_mobile:
            return self.state
        try:
            import js  # type: ignore
            egc = getattr(js.window, "EGC", None)
            inp = getattr(egc, "input", None) if egc is not None else None
            if inp is None:
                return self.state
            s = self.state
            s.move_x = float(getattr(inp, "moveX", 0.0) or 0.0)
            s.move_y = float(getattr(inp, "moveY", 0.0) or 0.0)
            s.look_dx = float(getattr(inp, "lookDX", 0.0) or 0.0)
            s.look_dy = float(getattr(inp, "lookDY", 0.0) or 0.0)
            s.jump = bool(getattr(inp, "jump", False))
            s.sneak = bool(getattr(inp, "sneak", False))
            s.fly_toggle = bool(getattr(inp, "flyToggle", False))
            s.break_held = bool(getattr(inp, "breakHeld", False))
            s.place_held = bool(getattr(inp, "placeHeld", False))
            s.inv_toggle = bool(getattr(inp, "invToggle", False))
            s.hotbar_index = int(getattr(inp, "hotbarIndex", 0) or 0)
        except Exception as exc:  # noqa: BLE001
            log.debug("TouchBridge poll failed: %r", exc)
        return self.state

    def poll(self) -> TouchInputState:
        return self._get_js_input() if self.is_mobile else self.state

    def apply_to_window(self, window) -> None:
        if not self.is_mobile:
            return
        s = self._get_js_input()
        keys = window.keys
        keys[pygame.K_w] = s.move_y > 0.3
        keys[pygame.K_s] = s.move_y < -0.3
        keys[pygame.K_d] = s.move_x > 0.3
        keys[pygame.K_a] = s.move_x < -0.3
        keys[pygame.K_SPACE] = s.jump
        keys[pygame.K_LSHIFT] = s.sneak
        window.mouse_buttons[1] = s.break_held
        window.mouse_buttons[3] = s.place_held
        window.mouse_rel = (int(s.look_dx), int(s.look_dy))

    def reset(self) -> None:
        self.state.reset_deltas()
