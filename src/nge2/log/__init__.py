"""Logging helpers. Root logger name is ``nge`` (not ``nge2``)."""

from __future__ import annotations

import logging
import os
import re
import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

_DEFAULT_LEVEL = os.environ.get("NGE_LOG_LEVEL", "INFO").upper()
_configured = False
_LOG_FORMAT = "%(asctime)s %(levelname)-7s %(message)s"
_LOG_DATEFMT = "%H:%M:%S"
_NGE_LOG_RE = re.compile(r"^nge-(\d+)\.log$", re.IGNORECASE)
_SHOT_RE = re.compile(r"^\d{6}-(\d+)\.jpg$", re.IGNORECASE)
_OVERLAY_MAX = 200
_screenshot_guard = threading.local()


def _configure_root() -> None:
    global _configured
    if _configured:
        return
    root = logging.getLogger("nge")
    # Do not clear existing handlers — hosts (e.g. NGE-STUDIO UI) may already
    # have attached bridges; wiping them drops live logs for the whole process.
    has_stream = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root.handlers
    )
    if not has_stream:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT))
        root.addHandler(handler)
    root.setLevel(_DEFAULT_LEVEL)
    root.propagate = False
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger under the ``nge`` root."""
    _configure_root()
    short = name.split(".")[-1]
    return logging.getLogger(f"nge.{short}")


def resolve_log_dir(log_dir: str | Path | None) -> Path:
    """Resolve absolute log root; default ``{cwd}/logs``."""
    if log_dir is None or str(log_dir).strip() == "":
        root = Path.cwd() / "logs"
    else:
        root = Path(log_dir)
        if not root.is_absolute():
            root = Path.cwd() / root
    return root.resolve()


def _pad_index(n: int) -> str:
    return f"{n:03d}" if n < 1000 else str(n)


def next_nge_log_index(day_dir: Path) -> int:
    highest = 0
    if day_dir.is_dir():
        for path in day_dir.glob("nge-*.log"):
            m = _NGE_LOG_RE.match(path.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def next_screenshot_index(screenshot_dir: Path) -> int:
    highest = 0
    if screenshot_dir.is_dir():
        for path in screenshot_dir.glob("*.jpg"):
            m = _SHOT_RE.match(path.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def allocate_log_file(log_dir: str | Path | None, *, when: datetime | None = None) -> Path:
    """Create day folder and return path to the next ``nge-NNN.log``."""
    root = resolve_log_dir(log_dir)
    day = (when or datetime.now()).strftime("%Y-%m-%d")
    day_dir = root / day
    day_dir.mkdir(parents=True, exist_ok=True)
    idx = next_nge_log_index(day_dir)
    path = day_dir / f"nge-{_pad_index(idx)}.log"
    path.touch(exist_ok=False)
    return path


def add_file_logging(
    log_dir: str | Path = ".",
    *,
    filename: str | None = None,
) -> Path:
    """Append a file handler (test helper / low-level). Prefer engine ``log_dir``."""
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


class ErrorScreenshotHandler(logging.Handler):
    """Invoke a callback for exact ERROR records only."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__(level=logging.ERROR)
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno != logging.ERROR:
            return
        if getattr(_screenshot_guard, "active", False):
            return
        try:
            _screenshot_guard.active = True
            self._callback(record.getMessage())
        except Exception:  # noqa: BLE001
            self.handleError(record)
        finally:
            _screenshot_guard.active = False


def attach_engine_logging(
    log_dir: str | Path | None,
    on_error: Callable[[str], None],
) -> tuple[Path, list[logging.Handler]]:
    """Attach per-instance file + ERROR screenshot handlers. Returns log path and handlers."""
    _configure_root()
    # Refresh console formatter (no module name) if root was configured earlier.
    root = logging.getLogger("nge")
    fmt = logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATEFMT)
    for h in root.handlers:
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler):
            h.setFormatter(fmt)

    log_path = allocate_log_file(log_dir)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    shot_handler = ErrorScreenshotHandler(on_error)
    root.addHandler(file_handler)
    root.addHandler(shot_handler)
    return log_path, [file_handler, shot_handler]


def detach_handlers(handlers: list[logging.Handler]) -> None:
    root = logging.getLogger("nge")
    for handler in handlers:
        try:
            root.removeHandler(handler)
            handler.close()
        except Exception:  # noqa: BLE001
            pass


def save_error_screenshot(
    frame_bgr,
    message: str,
    screenshot_dir: Path,
    *,
    when: datetime | None = None,
) -> Path:
    """Draw caption on BGR frame and save JPEG under ``screenshot_dir``."""
    from nge2.log._screenshot import annotate_and_save_jpeg

    screenshot_dir.mkdir(parents=True, exist_ok=True)
    now = when or datetime.now()
    idx = next_screenshot_index(screenshot_dir)
    path = screenshot_dir / f"{now.strftime('%H%M%S')}-{_pad_index(idx)}.jpg"
    text = message if len(message) <= _OVERLAY_MAX else message[:_OVERLAY_MAX] + "…"
    caption = f"{now.strftime('%Y-%m-%d %H:%M:%S')}  {text}"
    annotate_and_save_jpeg(frame_bgr, caption, path)
    return path


__all__ = [
    "ErrorScreenshotHandler",
    "add_file_logging",
    "allocate_log_file",
    "attach_engine_logging",
    "detach_handlers",
    "get_logger",
    "next_nge_log_index",
    "next_screenshot_index",
    "resolve_log_dir",
    "save_error_screenshot",
]
