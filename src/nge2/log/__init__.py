"""Logging helpers. Root logger name is ``nge`` (not ``nge2``)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

_DEFAULT_LEVEL = os.environ.get("NGE_LOG_LEVEL", "INFO").upper()
_configured = False
_LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_LOG_DATEFMT = "%H:%M:%S"


def _configure_root() -> None:
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
    root = logging.getLogger("nge")
    root.addHandler(handler)
    root.setLevel(_DEFAULT_LEVEL)
    root.propagate = False
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under the ``nge`` root."""
    _configure_root()
    short = name.split(".")[-1]
    return logging.getLogger(f"nge.{short}")


def add_file_logging(
    log_dir: str | Path = ".",
    *,
    filename: str | None = None,
) -> Path:
    """Append a file handler under ``log_dir`` (default file ``nge.log``).

    Returns the log file path. The same path is not attached twice.
    """
    _configure_root()
    directory = Path(log_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (filename or "nge.log")
    resolved = path.resolve()

    root = logging.getLogger("nge")
    for handler in root.handlers:
        if (
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename).resolve() == resolved
        ):
            return path

    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
    root.addHandler(file_handler)
    return path


def ensure_default_file_logging() -> Path:
    """Ensure cwd ``nge.log`` file logging is enabled."""
    return add_file_logging(".", filename="nge.log")
