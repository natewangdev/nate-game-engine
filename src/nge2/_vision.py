"""Shared vision search-region helpers (find / ocr / yolo)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from nge2._errors import FindError

if TYPE_CHECKING:
    from nge2.capture import Capture
    from nge2.window import Window


def validate_region(
    region: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int] | None:
    if region is None:
        return None
    if len(region) != 4:
        raise FindError(f"Invalid region (need 4 ints): {region!r}")
    x1, y1, x2, y2 = (int(v) for v in region)
    if x2 <= x1 or y2 <= y1:
        raise FindError(f"Invalid region (empty): {region!r}")
    return x1, y1, x2, y2


def search_screen_rect(
    window: Window,
    region: tuple[int, int, int, int] | None,
    frame_w: int,
    frame_h: int,
) -> tuple[int, int, int, int]:
    """Return search rect in screen pixels ``(l, t, r, b)`` clipped to frame."""
    client = window.client_region
    if region is None:
        if client is not None:
            l, t, r, b = client.screen
        else:
            l, t, r, b = 0, 0, frame_w, frame_h
    else:
        x1, y1, x2, y2 = region
        if client is not None:
            sl, st = window.client_to_screen(x1, y1)
            sr, sb = window.client_to_screen(x2, y2)
            l, t, r, b = int(sl), int(st), int(sr), int(sb)
        else:
            l, t, r, b = x1, y1, x2, y2

    l = max(0, min(int(l), frame_w))
    r = max(0, min(int(r), frame_w))
    t = max(0, min(int(t), frame_h))
    b = max(0, min(int(b), frame_h))
    if r <= l or b <= t:
        raise FindError("Search region is empty after clipping to frame")
    return l, t, r, b


def to_move_coords(window: Window, screen_x: float, screen_y: float) -> tuple[int, int]:
    if window.hwnd is not None:
        cx, cy = window.screen_to_client(screen_x, screen_y)
        return int(round(cx)), int(round(cy))
    return int(round(screen_x)), int(round(screen_y))


def grab_search(
    capture: Capture,
    window: Window,
    region: tuple[int, int, int, int] | None,
) -> tuple[np.ndarray, int, int]:
    """Fresh full grab + crop; return ``(crop_bgr, screen_l, screen_t)``."""
    region = validate_region(region)
    frame = capture.grab(region=None)
    h, w = frame.shape[:2]
    l, t, r, b = search_screen_rect(window, region, w, h)
    crop = frame[t:b, l:r]
    if crop.size == 0:
        raise FindError("Search crop is empty")
    return crop, l, t


def resolve_resource_path(resource_dir, path: str | object, *, required: bool) -> object | None:
    from pathlib import Path

    if path is None:
        if required:
            raise FileNotFoundError("path is required")
        return None
    p = Path(path)
    if not p.is_absolute():
        p = Path(resource_dir) / p
    p = p.resolve()
    if not p.is_file():
        if required:
            raise FileNotFoundError(str(p))
        return None
    return p
