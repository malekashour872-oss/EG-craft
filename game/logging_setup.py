# ═══ EG Craft ═══
# Copyright (c) 2025 Malik Hassan Ashour (مالك حسن عاشور). All rights reserved.
# Proprietary software. Copying, distribution, or modification without
# written permission is prohibited.
# هذا الملف مملوك ملكية مالك حسن عاشور — يُمنع النسخ أو التوزيع دون إذن

"""Logging setup for EG Craft.

Spec ref: §17.4 — logging_setup.py → logs/egcraft.log with timestamps
and tracebacks.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path


_INITIALISED = False
_LOG_PATH = Path("logs") / "egcraft.log"


def get_logger(name: str = "egcraft") -> logging.Logger:
    """Return the configured logger; idempotent."""
    global _INITIALISED
    logger = logging.getLogger(name)
    if _INITIALISED:
        return logger
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # File handler — append mode
    fh = logging.FileHandler(_LOG_PATH, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)

    # Stream handler — INFO to stdout
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    sh.setLevel(logging.INFO)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.propagate = False
    _INITIALISED = True
    return logger


def log_exception(logger: logging.Logger, exc: BaseException,
                  context: str = "") -> None:
    """Log an exception with full traceback."""
    import traceback
    msg = f"EXCEPTION during {context}: {exc!r}" if context else f"EXCEPTION: {exc!r}"
    logger.error(msg)
    tb = traceback.format_exc()
    for line in tb.splitlines():
        logger.debug(line)
