"""Process-level HID serial port exclusivity registry."""

from __future__ import annotations

from threading import Lock

_lock = Lock()
_held: set[str] = set()


def try_acquire(port: str) -> bool:
    """Return True if ``port`` was acquired; False if already held."""
    key = port.upper()
    with _lock:
        if key in _held:
            return False
        _held.add(key)
        return True


def release(port: str | None) -> None:
    if not port:
        return
    key = port.upper()
    with _lock:
        _held.discard(key)


def clear() -> None:
    """Test helper: drop all held ports."""
    with _lock:
        _held.clear()
