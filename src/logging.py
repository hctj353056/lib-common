"""Logging setup helpers; configuration is opt-in and never replaces handlers by default."""
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or "lib_common")


def configure_logging(level: int = logging.INFO, fmt: str = "%(asctime)s %(levelname)s %(name)s: %(message)s", *, force: bool = False) -> logging.Logger:
    """Configure the root logger once. Set force=True to replace existing handlers."""
    logging.basicConfig(level=level, format=fmt, force=force)
    return logging.getLogger("lib_common")
