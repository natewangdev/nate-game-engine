#!/usr/bin/env python3
"""Hardware smoke: window find / activate / topmost / move.

Requires ESP32-S3 for NGE2 construct and a real desktop. Does not run in CI.

Edit constants below, then::

    uv run python examples/window_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
HWND: int | None = None  # optional bound hwnd; find still works when None
HUMANIZE = True
CAPTURE = "dxcam"
RESOURCE_DIR = Path(__file__).resolve().parent
YOLO_MODEL = "models/best.onnx"  # required at construct for current NGE2
TITLE_QUERY = "暗黑破坏神"  # case-insensitive substring
DO_ACTIVATE = True
DO_TOPMOST = False  # set True then False below if you want a pin cycle
DO_MOVE = True
MOVE_XY = (0, 0)  # outer-frame screen physical pixels
USE_FIRST_MATCH = True  # if True, ops use first find hit; else bound HWND
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError, WindowError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(f"NGE2 window smoke: hwnd={HWND!r} query={TITLE_QUERY!r}")
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

    bound_before = engine.window.hwnd
    try:
        matches = engine.window.find_by_title(TITLE_QUERY)
        print(f"find_by_title -> {len(matches)} match(es); bound hwnd still {engine.window.hwnd!r}")
        for i, m in enumerate(matches[:10], 1):
            print(f"  {i}. hwnd={m.hwnd} title={m.title!r} rect={m.rect}")

        if engine.window.hwnd != bound_before:
            print("ERROR: find rebinding bound hwnd", file=sys.stderr)
            return 1

        target: int | None
        if USE_FIRST_MATCH:
            if not matches:
                print("No matches; skip activate/topmost/move", file=sys.stderr)
                return 0
            target = matches[0].hwnd
        else:
            target = None  # use bound

        if DO_ACTIVATE:
            engine.window.activate(hwnd=target)
            print(f"activate hwnd={target if target is not None else bound_before}")

        if DO_TOPMOST:
            engine.window.set_topmost(True, hwnd=target)
            print("set_topmost True")
            engine.window.set_topmost(False, hwnd=target)
            print("set_topmost False")

        if DO_MOVE:
            x, y = MOVE_XY
            engine.window.move(x, y, hwnd=target)
            print(f"move outer frame to ({x}, {y})")

        if engine.window.hwnd != bound_before:
            print("ERROR: ops rebinding bound hwnd", file=sys.stderr)
            return 1
    except WindowError as exc:
        print(f"WindowError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
