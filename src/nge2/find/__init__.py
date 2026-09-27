"""Find-image / find-color (OpenCV template match + color scan)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from nge2._errors import FindError
from nge2.log import get_logger

if TYPE_CHECKING:
    from nge2.capture import Capture
    from nge2.window import Window

log = get_logger(__name__)

DEFAULT_THRESHOLD = 0.7
DEFAULT_COLOR_TOLERANCE = 10
_MAX_COLOR_HITS = 500
_NMS_IOU = 0.3


@dataclass(frozen=True)
class Match:
    """Template match center in move-aligned coordinates."""

    x: int
    y: int
    score: float
    width: int
    height: int


@dataclass(frozen=True)
class ColorMatch:
    """Color hit in move-aligned coordinates."""

    x: int
    y: int
    color: tuple[int, int, int]


def _imread_bgr(path: Path) -> np.ndarray:
    """Load BGR image; supports non-ASCII paths on Windows."""
    import cv2

    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        raise FindError(f"Failed to read image: {path}")
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise FindError(f"Failed to decode image: {path}")
    return img


def _parse_color(color: object) -> tuple[int, int, int]:
    if isinstance(color, str):
        s = color.strip().removeprefix("#")
        if len(s) != 6:
            raise ValueError(f"Invalid color string: {color!r}")
        try:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
        except ValueError as exc:
            raise ValueError(f"Invalid color string: {color!r}") from exc
        return r, g, b
    if isinstance(color, (tuple, list)) and len(color) == 3:
        try:
            r, g, b = (int(c) for c in color)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid color tuple: {color!r}") from exc
        for c in (r, g, b):
            if c < 0 or c > 255:
                raise ValueError(f"Color channel out of range: {color!r}")
        return r, g, b
    raise ValueError(f"Invalid color: {color!r}")


def _box_iou(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _nms_matches(
    candidates: list[tuple[float, int, int, int, int]],
    iou_thresh: float = _NMS_IOU,
) -> list[tuple[float, int, int, int, int]]:
    """``(score, left, top, width, height)`` → non-overlapping, score desc."""
    ordered = sorted(candidates, key=lambda c: c[0], reverse=True)
    kept: list[tuple[float, int, int, int, int]] = []
    for score, left, top, w, h in ordered:
        box = (left, top, left + w, top + h)
        if any(
            _box_iou(box, (kl, kt, kl + kw, kt + kh)) > iou_thresh
            for _, kl, kt, kw, kh in kept
        ):
            continue
        kept.append((score, left, top, w, h))
    return kept


class Find:
    """Engine-bound find-image / find-color facade."""

    def __init__(
        self,
        *,
        resource_dir: str | Path,
        capture: Capture,
        window: Window,
    ) -> None:
        self._resource_dir = Path(resource_dir)
        self._capture = capture
        self._window = window

    def _resolve_template(self, path: str | Path) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self._resource_dir / p
        p = p.resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Template not found: {p}")
        return p

    def _validate_region(
        self, region: tuple[int, int, int, int] | None
    ) -> tuple[int, int, int, int] | None:
        if region is None:
            return None
        if len(region) != 4:
            raise FindError(f"Invalid region (need 4 ints): {region!r}")
        x1, y1, x2, y2 = (int(v) for v in region)
        if x2 <= x1 or y2 <= y1:
            raise FindError(f"Invalid region (empty): {region!r}")
        return x1, y1, x2, y2

    def _search_screen_rect(
        self,
        region: tuple[int, int, int, int] | None,
        frame_w: int,
        frame_h: int,
    ) -> tuple[int, int, int, int]:
        """Return search rect in screen pixels ``(l, t, r, b)`` clipped to frame."""
        client = self._window.client_region
        if region is None:
            if client is not None:
                l, t, r, b = client.screen
            else:
                l, t, r, b = 0, 0, frame_w, frame_h
        else:
            x1, y1, x2, y2 = region
            if client is not None:
                sl, st = self._window.client_to_screen(x1, y1)
                sr, sb = self._window.client_to_screen(x2, y2)
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

    def _to_move_coords(self, screen_x: float, screen_y: float) -> tuple[int, int]:
        if self._window.hwnd is not None:
            cx, cy = self._window.screen_to_client(screen_x, screen_y)
            return int(round(cx)), int(round(cy))
        return int(round(screen_x)), int(round(screen_y))

    def _grab_search(
        self, region: tuple[int, int, int, int] | None
    ) -> tuple[np.ndarray, int, int]:
        """Fresh full grab, crop search area; return ``(crop, screen_l, screen_t)``."""
        frame = self._capture.grab(region=None)
        h, w = frame.shape[:2]
        l, t, r, b = self._search_screen_rect(region, w, h)
        crop = frame[t:b, l:r]
        if crop.size == 0:
            raise FindError("Search crop is empty")
        return crop, l, t

    def find_image(
        self,
        path: str | Path,
        *,
        threshold: float = DEFAULT_THRESHOLD,
        region: tuple[int, int, int, int] | None = None,
    ) -> Match | None:
        matches = self._match_all(path, threshold=threshold, region=region, multi=False)
        return matches[0] if matches else None

    def find_images(
        self,
        path: str | Path,
        *,
        threshold: float = DEFAULT_THRESHOLD,
        region: tuple[int, int, int, int] | None = None,
    ) -> list[Match]:
        return self._match_all(path, threshold=threshold, region=region, multi=True)

    def _match_all(
        self,
        path: str | Path,
        *,
        threshold: float,
        region: tuple[int, int, int, int] | None,
        multi: bool,
    ) -> list[Match]:
        import cv2

        region = self._validate_region(region)
        tmpl_path = self._resolve_template(path)
        template = _imread_bgr(tmpl_path)
        th, tw = template.shape[:2]
        crop, off_x, off_y = self._grab_search(region)
        ch, cw = crop.shape[:2]
        if th > ch or tw > cw:
            log.debug("Template larger than search region (%sx%s > %sx%s)", tw, th, cw, ch)
            return []

        result = cv2.matchTemplate(crop, template, cv2.TM_CCOEFF_NORMED)
        if not multi:
            _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val < threshold:
                return []
            left, top = int(max_loc[0]), int(max_loc[1])
            cx = off_x + left + tw / 2.0
            cy = off_y + top + th / 2.0
            mx, my = self._to_move_coords(cx, cy)
            return [
                Match(x=mx, y=my, score=float(max_val), width=tw, height=th),
            ]

        ys, xs = np.where(result >= threshold)
        candidates: list[tuple[float, int, int, int, int]] = []
        for y, x in zip(ys.tolist(), xs.tolist(), strict=False):
            candidates.append((float(result[y, x]), int(x), int(y), tw, th))
        kept = _nms_matches(candidates)
        out: list[Match] = []
        for score, left, top, w, h in kept:
            cx = off_x + left + w / 2.0
            cy = off_y + top + h / 2.0
            mx, my = self._to_move_coords(cx, cy)
            out.append(Match(x=mx, y=my, score=score, width=w, height=h))
        return out

    def find_color(
        self,
        color: object,
        *,
        tolerance: int = DEFAULT_COLOR_TOLERANCE,
        region: tuple[int, int, int, int] | None = None,
        multi: bool = False,
    ) -> ColorMatch | None | list[ColorMatch]:
        rgb = _parse_color(color)
        if tolerance < 0:
            raise FindError(f"Invalid tolerance: {tolerance}")
        region = self._validate_region(region)
        crop, off_x, off_y = self._grab_search(region)

        target_bgr = np.array([rgb[2], rgb[1], rgb[0]], dtype=np.int16)
        diff = np.abs(crop.astype(np.int16) - target_bgr)
        mask = np.all(diff <= int(tolerance), axis=2)
        ys, xs = np.where(mask)
        if ys.size == 0:
            return [] if multi else None

        if not multi:
            # First hit in row-major order (numpy where is row-major).
            sx = off_x + int(xs[0])
            sy = off_y + int(ys[0])
            mx, my = self._to_move_coords(sx, sy)
            return ColorMatch(x=mx, y=my, color=rgb)

        hits: list[ColorMatch] = []
        n = min(int(ys.size), _MAX_COLOR_HITS)
        for i in range(n):
            sx = off_x + int(xs[i])
            sy = off_y + int(ys[i])
            mx, my = self._to_move_coords(sx, sy)
            hits.append(ColorMatch(x=mx, y=my, color=rgb))
        return hits


__all__ = [
    "DEFAULT_COLOR_TOLERANCE",
    "DEFAULT_THRESHOLD",
    "ColorMatch",
    "Find",
    "Match",
]
