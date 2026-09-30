#!/usr/bin/env python3
"""Hardware smoke: YOLO detect with timeout_ms / interval_ms poll.

Requires ESP32-S3 and ONNX under resource_dir (see examples/models/).
Polls until a non-empty detection list or deadline (miss -> []).

    uv run python examples/yolo_wait_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
HWND = 460458
HUMANIZE = True
CAPTURE = "dxcam"
RESOURCE_DIR = Path(__file__).resolve().parent
YOLO_MODEL = "models/best.onnx"
YOLO_NAMES = "models/yolo.names"
REGION = None  # (x1,y1,x2,y2) or None
CONF = 0.25
IOU = 0.45
TIMEOUT_MS = 5000  # 0 = one attempt; >0 = poll until non-empty or deadline
INTERVAL_MS = 500
MOVE_TO_FIRST = False
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(
        f"NGE2 yolo_wait smoke: hwnd={HWND!r} model={YOLO_MODEL} "
        f"timeout_ms={TIMEOUT_MS} interval_ms={INTERVAL_MS} conf={CONF}"
    )
    try:
        engine = nge2.NGE2(
            resource_dir=RESOURCE_DIR,
            capture=CAPTURE,
            hwnd=HWND,
            humanize=HUMANIZE,
            yolo_model=YOLO_MODEL,
            yolo_names=YOLO_NAMES,
        )
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        print("Place ONNX under examples/models/", file=sys.stderr)
        return 1

    try:
        hits = engine.yolo.detect(
            conf=CONF,
            iou=IOU,
            region=REGION,
            timeout_ms=TIMEOUT_MS,
            interval_ms=INTERVAL_MS,
        )
        print(f"detect(timeout_ms={TIMEOUT_MS}) -> {len(hits)} hit(s)")
        for i, d in enumerate(hits[:10], 1):
            print(f"  {i}. {d}")
        if not hits:
            print("empty list (no detections within timeout)", file=sys.stderr)
            return 1
        if MOVE_TO_FIRST:
            engine.control.move(hits[0].x, hits[0].y)
            print(f"moved to ({hits[0].x}, {hits[0].y})")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
