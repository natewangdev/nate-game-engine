#!/usr/bin/env python3
"""Hardware smoke test: mouse scroll via ESP32-S3 HID.

Requires a connected device. Does not run in CI.

Scroll acts at the **current** pointer position (does not move the mouse by itself).
Optionally move first with ``MOVE_TO``, then run ``SCROLLS``.

Edit the constants below, then from repo root::

    uv run python examples/scroll_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
# Optional pre-move so the wheel targets a control under the cursor.
# None = leave pointer where it is; (x, y) = client-relative if HWND set.
MOVE_TO = (1301,472)
DURATION = 0.5
SPREAD = 0.0
# Each item: (direction, notches) — direction "up" | "down"; notches >= 1
SCROLLS = [
    ("down", 10),
]
HWND = 132884  # None = screen coords for MOVE_TO; int = client-relative
HUMANIZE = True
CAPTURE = "dxcam"  # "dxcam" | "mss"
RESOURCE_DIR = Path(".")
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(
        f"NGE2 scroll smoke: move_to={MOVE_TO!r} scrolls={SCROLLS} "
        f"hwnd={HWND!r} humanize={HUMANIZE}"
    )

    try:
        engine = nge2.NGE2(
            resource_dir=RESOURCE_DIR,
            capture=CAPTURE,
            hwnd=HWND,
            humanize=HUMANIZE,
        )
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        return 1

    try:
        if HWND is not None:
            print(f"window title={engine.window.title!r}")
            print(f"client_region={engine.window.client_region}")
        if MOVE_TO is not None:
            x, y = MOVE_TO
            duration = None if not HUMANIZE else DURATION
            spread = 0.0 if not HUMANIZE else SPREAD
            engine.control.move(x, y, duration=duration, spread=spread)
            engine.time.sleep(1000)
            print(f"moved -> ({x}, {y})")
        for i, (direction, notches) in enumerate(SCROLLS, start=1):
            engine.control.scroll(direction, notches)
            print(f"scroll {i}/{len(SCROLLS)} done -> {direction!r} x{notches}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
