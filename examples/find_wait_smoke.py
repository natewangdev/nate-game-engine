#!/usr/bin/env python3
"""Hardware smoke: find_image with timeout_ms / interval_ms poll.

Requires ESP32-S3 and a display. Does not run in CI.

Flow: grab → save self-template → find_image(..., timeout_ms=...) until hit
or deadline.

    uv run python examples/find_wait_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
HWND = 460458  # None = screen coords; int = client-relative
HUMANIZE = True
CAPTURE = "dxcam"
RESOURCE_DIR = Path(__file__).resolve().parent
YOLO_MODEL = "models/best.onnx"
# Crop from grab used as self-template (l, t, r, b) in move-aligned space
TEMPLATE_REGION = (1367,563,1397,592)
TEMPLATE_NAME = "_find_wait_smoke_tmpl.png"
THRESHOLD = 0.7
TIMEOUT_MS = 5000  # 0 = one attempt
INTERVAL_MS = 500
MOVE_TO_MATCH = True
# ------------------


def main() -> int:
    try:
        import cv2
        import nge2
        from nge2._errors import ConstructError
    except ImportError as exc:
        print(f"Import failed: {exc}. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(
        f"NGE2 find_wait smoke: hwnd={HWND!r} timeout_ms={TIMEOUT_MS} "
        f"interval_ms={INTERVAL_MS} threshold={THRESHOLD}"
    )
    try:
        engine = nge2.NGE2(
            resource_dir=RESOURCE_DIR,
            capture=CAPTURE,
            hwnd=HWND,
            humanize=HUMANIZE,
            yolo_model=YOLO_MODEL,
        )
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        return 1

    try:
        # Hide-style check: first call should succeed quickly with self-template.
        match = engine.find.find_image(
            TEMPLATE_NAME,
            threshold=THRESHOLD,
            timeout_ms=TIMEOUT_MS,
            interval_ms=INTERVAL_MS,
        )
        print(f"find_image(timeout_ms={TIMEOUT_MS}) -> {match}")
        if match is None:
            print("miss within timeout (unexpected for self-template)", file=sys.stderr)
            return 1

        if MOVE_TO_MATCH:
            engine.control.move(match.x, match.y)
            print(f"moved to ({match.x}, {match.y})")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
