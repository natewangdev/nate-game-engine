#!/usr/bin/env python3
"""Hardware smoke: YOLO detect via onnxruntime.

Requires ESP32-S3 and ONNX under resource_dir (see examples/models/).

    uv run python examples/yolo_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
HWND = 524832
HUMANIZE = True
CAPTURE = "dxcam"
RESOURCE_DIR = Path(__file__).resolve().parent  # expects models/ beside this file
YOLO_MODEL = "models/best.onnx"
YOLO_NAMES = "models/yolo.names"
REGION = None  # (x1,y1,x2,y2) or None
CONF = 0.25
IOU = 0.45
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(f"NGE2 yolo smoke: hwnd={HWND!r} model={YOLO_MODEL} conf={CONF}")
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
        print("Place ONNX under examples/models/ (see examples/models/README.md)", file=sys.stderr)
        return 1

    try:
        hits = engine.yolo.detect(conf=CONF, iou=IOU, region=REGION)
        print(f"detect -> {len(hits)} hit(s)")
        for i, d in enumerate(hits[:10], 1):
            print(f"  {i}. {d}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
