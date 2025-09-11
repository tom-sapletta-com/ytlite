#!/usr/bin/env python3
"""
Centralized logging setup for YTLite
- File + console logging
- Rotating file handler in logs/ytlite.log
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "ytlite.log"

_configured = False

def _ensure_handlers():
    global _configured
    if _configured:
        return

    logger = logging.getLogger("ytlite")
    logger.setLevel(getattr(logging, DEFAULT_LEVEL, logging.INFO))

    # File handler (rotating)
    fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(getattr(logging, DEFAULT_LEVEL, logging.INFO))
    ffmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    fh.setFormatter(ffmt)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, DEFAULT_LEVEL, logging.INFO))
    cfmt = logging.Formatter("%(levelname)s [%(name)s] %(message)s")
    ch.setFormatter(cfmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    _ensure_handlers()
    return logging.getLogger("ytlite").getChild(name)
