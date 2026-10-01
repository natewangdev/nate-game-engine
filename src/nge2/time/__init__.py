"""Millisecond sleep helpers (fixed and uniform random). Stateless."""

from __future__ import annotations

import random
import time as _stdlib_time
from typing import overload


def _sleep(seconds: float) -> None:
    """Sleep seam for unit tests."""
    _stdlib_time.sleep(seconds)


def _randint(a: int, b: int) -> int:
    """Inclusive random integer seam for unit tests."""
    return random.randint(a, b)


def _as_ms(value: object, *, label: str) -> int:
    """Require a non-negative int millisecond duration (reject bool)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be a non-negative int (milliseconds), got {value!r}")
    if value < 0:
        raise ValueError(f"{label} must be >= 0, got {value}")
    return value


@overload
def sleep(ms: int, /) -> int: ...


@overload
def sleep(min_ms: int, max_ms: int, /) -> int: ...


def sleep(*args: int) -> int:
    """Sleep a fixed or uniform random duration in milliseconds.

    * ``sleep(ms)`` — fixed delay; returns ``ms``.
    * ``sleep(min_ms, max_ms)`` — uniform closed interval; returns sampled ``int``.
    """
    if len(args) == 1:
        duration = _as_ms(args[0], label="ms")
    elif len(args) == 2:
        min_ms = _as_ms(args[0], label="min_ms")
        max_ms = _as_ms(args[1], label="max_ms")
        if min_ms > max_ms:
            raise ValueError(f"min_ms ({min_ms}) must be <= max_ms ({max_ms})")
        duration = _randint(min_ms, max_ms)
    else:
        raise ValueError("sleep requires 1 argument (ms) or 2 arguments (min_ms, max_ms)")

    if duration > 0:
        _sleep(duration / 1000.0)
    return duration


delay = sleep


class Time:
    """Stateless time facade (also exposed as ``engine.time``)."""

    sleep = staticmethod(sleep)
    delay = staticmethod(sleep)


__all__ = ["Time", "delay", "sleep"]
