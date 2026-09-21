# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Top-level settings dataclass for EG Craft.

Spec ref: §4 — settings.py defaults.
Loaded/saved as JSON via :func:`load` / :func:`save`.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Settings:
    width: int = 1280
    height: int = 720
    fov: float = 70.0
    render_distance: int = 4
    master_volume: float = 0.8
    sfx: float = 1.0
    music: float = 0.4
    sensitivity: float = 0.0022
    fullscreen: bool = False
    seed: int = 12345
    vsync: bool = True
    mouse_sensitivity: float = 0.0022  # alias for sensitivity

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        clean = {k: v for k, v in data.items() if k in known}
        return cls(**clean)


def default_path() -> Path:
    here = Path(__file__).resolve().parent
    return here / "assets" / "settings.json"


def load(path: Path | str | None = None) -> Settings:
    p = Path(path) if path else default_path()
    if not p.exists():
        s = Settings()
        save(s, p)
        return s
    try:
        with p.open("r", encoding="utf-8") as fh:
            return Settings.from_dict(json.load(fh))
    except (json.JSONDecodeError, OSError):
        return Settings()


def save(settings: Settings, path: Path | str | None = None) -> None:
    p = Path(path) if path else default_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        json.dump(settings.to_dict(), fh, indent=2, ensure_ascii=False)
