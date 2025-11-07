"""Configuração básica de logging centralizada.

Uso:
    from src.utils.logging_config import get_logger
    logger = get_logger(__name__)
"""
from __future__ import annotations
import logging
import os

_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def _configure_root_once() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=_LEVEL,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

_configure_root_once()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
