#!/usr/bin/env python3
"""Smoke test for nge2.time sleep / delay (no ESP32 required).

Demonstrates module import, ``Time`` static methods, and optionally
``engine.time`` when hardware is available.

From repo root::

    uv run python examples/time_smoke.py
"""

from __future__ import annotations

import sys

# --- edit these ---
FIXED_MS = 50
RANDOM_MIN_MS = 20
RANDOM_MAX_MS = 80
# Set True + HWND/port if you also want to exercise engine.time (needs ESP32).
USE_ENGINE = False
HWND = None
CAPTURE = "dxcam"
# ------------------


def main() -> int:
    try:
        from nge2.time import Time, delay, sleep
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(f"time smoke: fixed={FIXED_MS}ms random=[{RANDOM_MIN_MS},{RANDOM_MAX_MS}]ms")

    fixed = sleep(FIXED_MS)
    print(f"sleep({FIXED_MS}) -> {fixed}")
    assert fixed == FIXED_MS

    zero = Time.sleep(0)
    print(f"Time.sleep(0) -> {zero}")
    assert zero == 0

    sampled = delay(RANDOM_MIN_MS, RANDOM_MAX_MS)
    print(f"delay({RANDOM_MIN_MS}, {RANDOM_MAX_MS}) -> {sampled}")
    assert RANDOM_MIN_MS <= sampled <= RANDOM_MAX_MS

    if not USE_ENGINE:
        print("OK (import / Time surfaces; set USE_ENGINE=True for engine.time)")
        return 0

    try:
        import nge2
        from nge2._errors import ConstructError
        from pathlib import Path

        engine = nge2.NGE2(
            resource_dir=Path("examples"),
            capture=CAPTURE,
            hwnd=HWND,
            log_dir=Path("logs"),
        )
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        return 1

    try:
        got = engine.time.sleep(FIXED_MS)
        print(f"engine.time.sleep({FIXED_MS}) -> {got}")
        assert got == FIXED_MS
        rnd = engine.time.delay(RANDOM_MIN_MS, RANDOM_MAX_MS)
        print(f"engine.time.delay(...) -> {rnd}")
        assert RANDOM_MIN_MS <= rnd <= RANDOM_MAX_MS
    finally:
        engine.close()

    print("OK (including engine.time)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
