"""OCR via RapidOCR (legacy nge-compatible stack), eager per NGE2 instance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nge2._errors import ClosedError, ConstructError, FindError
from nge2._vision import grab_search, to_move_coords, validate_region
from nge2.log import get_logger

if TYPE_CHECKING:
    from nge2.capture import Capture
    from nge2.window import Window

log = get_logger(__name__)

_MIN_SIDE = 16


@dataclass(frozen=True)
class OcrLine:
    """OCR line in move-aligned coordinates."""

    text: str
    score: float
    x: int
    y: int
    box: tuple[int, int, int, int]


def _points_to_aabb(
    pts: list[tuple[int, int]],
) -> tuple[int, int, int, int]:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


class Ocr:
    """Engine-bound OCR facade backed by RapidOCR."""

    def __init__(
        self,
        *,
        capture: Capture,
        window: Window,
        engine_kwargs: dict[str, Any] | None = None,
        engine: object | None = None,
    ) -> None:
        self._capture = capture
        self._window = window
        self._closed = False
        if engine is not None:
            self._engine = engine
            log.info("OCR engine ready (injected)")
            return
        try:
            from rapidocr_onnxruntime import RapidOCR
        except Exception as exc:
            raise ConstructError(
                "RapidOCR is not available (install rapidocr-onnxruntime)"
            ) from exc
        try:
            self._engine = RapidOCR(**(engine_kwargs or {}))
        except Exception as exc:
            raise ConstructError(f"Failed to initialize RapidOCR: {exc}") from exc
        log.info("OCR engine ready (RapidOCR)")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._engine = None
        log.info("OCR engine released")

    def _ensure_open(self) -> None:
        if self._closed:
            raise ClosedError("OCR is closed; create a new NGE2 instance")

    def recognize(
        self,
        *,
        region: tuple[int, int, int, int] | None = None,
        min_score: float = 0.0,
    ) -> list[OcrLine]:
        self._ensure_open()
        region = validate_region(region)
        crop, off_x, off_y = grab_search(self._capture, self._window, region)
        ch, cw = crop.shape[:2]
        if ch < _MIN_SIDE or cw < _MIN_SIDE:
            log.debug("OCR skip: crop %sx%s below min %s", cw, ch, _MIN_SIDE)
            return []

        try:
            raw, _ = self._engine(crop)  # type: ignore[operator]
        except Exception as exc:
            raise FindError(f"OCR inference failed: {exc}") from exc

        lines: list[OcrLine] = []
        if not raw:
            return lines
        for box, text, score in raw:
            score_f = float(score)
            if score_f < min_score:
                continue
            pts = [(int(px) + off_x, int(py) + off_y) for px, py in box]
            x1, y1, x2, y2 = _points_to_aabb(pts)
            mx1, my1 = to_move_coords(self._window, x1, y1)
            mx2, my2 = to_move_coords(self._window, x2, y2)
            cx = (mx1 + mx2) / 2.0
            cy = (my1 + my2) / 2.0
            lines.append(
                OcrLine(
                    text=str(text),
                    score=score_f,
                    x=int(round(cx)),
                    y=int(round(cy)),
                    box=(mx1, my1, mx2, my2),
                )
            )
        lines.sort(key=lambda ln: ln.score, reverse=True)
        return lines


__all__ = ["Ocr", "OcrLine"]
