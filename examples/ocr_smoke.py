#!/usr/bin/env python3
"""Hardware smoke: OCR recognize via RapidOCR.

Requires ESP32-S3. RapidOCR loads default models (no ocr_det/rec paths).
YOLO still needs an ONNX under resource_dir for NGE2 construct.

    uv run python examples/ocr_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
HWND = 524832
HUMANIZE = True
CAPTURE = "dxcam"
RESOURCE_DIR = Path(__file__).resolve().parent
YOLO_MODEL = "models/best.onnx"  # required at construct (even for OCR-only smoke)
# Each item: (x1, y1, x2, y2) client-relative if HWND set; None = full client/screen
REGIONS = [
    (1079,816,1219,844),
    (1270,816,1333,843),  # edit second region
]
OCR_KWARGS = None  # optional dict forwarded to RapidOCR(...)
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(f"NGE2 ocr smoke: hwnd={HWND!r} regions={len(REGIONS)} (RapidOCR defaults)")
    try:
        engine = nge2.NGE2(
            resource_dir=RESOURCE_DIR,
            capture=CAPTURE,
            hwnd=HWND,
            humanize=HUMANIZE,
            yolo_model=YOLO_MODEL,
            ocr_kwargs=OCR_KWARGS,
        )
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        print(
            "Need YOLO ONNX under examples/models/ for construct; "
            "OCR uses RapidOCR built-in models.",
            file=sys.stderr,
        )
        return 1

    try:
        for ri, region in enumerate(REGIONS, start=1):
            lines = engine.ocr.recognize(region=region)
            print(f"region {ri}/{len(REGIONS)} {region!r} -> {len(lines)} line(s)")
            for i, ln in enumerate(lines[:10], 1):
                print(f"  {i}. {ln!r}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
