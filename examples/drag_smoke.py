#!/usr/bin/env python3
"""Hardware smoke test: drag via ESP32-S3 HID.

Requires a connected device. Does not run in CI.

Edit the constants below, then from repo root::

    uv run python examples/drag_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
# Each item: (x1, y1, x2, y2) — start then end (client-relative if HWND set)
DRAGS = [
    (593,483, 321,842),
]
DURATION = 1
SPREAD = 0.0
BUTTON = None  # "L" | "R"
HWND = 262834  # None = screen coords; int = client-relative
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
        f"NGE2 drag smoke: drags={DRAGS} duration={DURATION} "
        f"spread={SPREAD} button={BUTTON!r} hwnd={HWND!r} humanize={HUMANIZE}"
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
        duration = None if not HUMANIZE else DURATION
        spread = 0.0 if not HUMANIZE else SPREAD
        for i, (x1, y1, x2, y2) in enumerate(DRAGS, start=1):
            engine.control.drag(
                x1,
                y1,
                x2,
                y2,
            )
            print(f"drag {i}/{len(DRAGS)} done -> ({x1}, {y1}) -> ({x2}, {y2})")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
