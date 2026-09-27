#!/usr/bin/env python3
"""Hardware smoke: find_image / find_color via live capture.

Requires ESP32-S3 (NGE2 construct) and a display. Does not run in CI.

Flow: grab → crop a patch as template under resource_dir → find_image /
find_color → print results (optional move to match).

Edit constants below, then::

    uv run python examples/find_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
HWND = 262834  # None = screen coords; int = client-relative
HUMANIZE = True
CAPTURE = "dxcam"  # "dxcam" | "mss"
RESOURCE_DIR = Path(".")
# Crop from grab used as self-template (l, t, r, b) in move-aligned space
TEMPLATE_REGION = (190,332,292,357)
TEMPLATE_NAME = "_find_smoke_tmpl.png"
THRESHOLD = 0.7
COLOR = "#710A07"  # e.g. (255, 0, 0) or "#FF0000"; None = skip find_color
COLOR_TOLERANCE = 0
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
        f"NGE2 find smoke: hwnd={HWND!r} capture={CAPTURE} "
        f"region={TEMPLATE_REGION} threshold={THRESHOLD}"
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

        frame = engine.capture.grab(region=None)
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = TEMPLATE_REGION
        if HWND is not None:
            sl, st = engine.window.client_to_screen(x1, y1)
            sr, sb = engine.window.client_to_screen(x2, y2)
            l, t, r, b = int(sl), int(st), int(sr), int(sb)
        else:
            l, t, r, b = x1, y1, x2, y2
        l = max(0, min(l, w))
        r = max(0, min(r, w))
        t = max(0, min(t, h))
        b = max(0, min(b, h))
        if r <= l or b <= t:
            print("TEMPLATE_REGION empty after clip", file=sys.stderr)
            return 1
        patch = frame[t:b, l:r]
        out = Path(RESOURCE_DIR).resolve() / TEMPLATE_NAME
        ok, buf = cv2.imencode(".png", patch)
        if not ok:
            print("Failed to encode template", file=sys.stderr)
            return 1
        out.write_bytes(buf.tobytes())
        print(f"wrote template {out} size={patch.shape[1]}x{patch.shape[0]}")

        match = engine.find.find_image(TEMPLATE_NAME, threshold=THRESHOLD)
        print(f"find_image -> {match}")
        if match is None:
            print("find_image miss (unexpected for self-template)", file=sys.stderr)
            return 1

        multi = engine.find.find_images(TEMPLATE_NAME, threshold=THRESHOLD)
        print(f"find_images -> {len(multi)} hit(s)")

        if COLOR is not None:
            c = engine.find.find_color(COLOR, tolerance=COLOR_TOLERANCE,region=TEMPLATE_REGION)
            print(f"find_color({COLOR!r}) -> {c}")

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
