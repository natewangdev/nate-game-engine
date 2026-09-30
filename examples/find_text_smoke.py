#!/usr/bin/env python3
"""Hardware smoke: OCR find_text (substring + optional poll).

Requires ESP32-S3. RapidOCR loads default models.
YOLO ONNX still needed under resource_dir for NGE2 construct.

    uv run python examples/find_text_smoke.py
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
TEXT = "路西法"  # case-insensitive substring
REGION = (1056,75,1580,829)  # (x1, y1, x2, y2) or None = full client/screen
MULTI = False  # False -> first OcrLine | None; True -> list
TIMEOUT_MS = 20000  # 0 = one attempt; >0 = poll until match or deadline
INTERVAL_MS = 1000
MIN_SCORE = 0.0
MOVE_TO_MATCH = True
OCR_KWARGS = None
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(
        f"NGE2 find_text smoke: hwnd={HWND!r} text={TEXT!r} "
        f"timeout_ms={TIMEOUT_MS} interval_ms={INTERVAL_MS} multi={MULTI}"
    )
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
        return 1

    try:
        got = engine.ocr.find_text(
            TEXT,
            region=REGION,
            multi=MULTI,
            timeout_ms=TIMEOUT_MS,
            interval_ms=INTERVAL_MS,
            min_score=MIN_SCORE,
        )
        if MULTI:
            print(f"find_text -> {len(got)} line(s)")
            for i, ln in enumerate(got[:10], 1):
                print(f"  {i}. {ln!r}")
            first = got[0] if got else None
        else:
            print(f"find_text -> {got!r}")
            first = got

        if first is None:
            print("no match (None / empty within timeout)", file=sys.stderr)
            return 1

        if MOVE_TO_MATCH:
            engine.control.move(first.x, first.y)
            print(f"moved to ({first.x}, {first.y})")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
