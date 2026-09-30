"""YOLO object detection via onnxruntime (YOLOv8-detect style)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from nge2._errors import ClosedError, ConstructError, FindError
from nge2._vision import grab_search, poll_until, to_move_coords, validate_region
from nge2.log import get_logger

if TYPE_CHECKING:
    from nge2.capture import Capture
    from nge2.window import Window

log = get_logger(__name__)

DEFAULT_CONF = 0.25
DEFAULT_IOU = 0.45
_MIN_SIDE = 32


@dataclass(frozen=True)
class Detection:
    """YOLO detection in move-aligned coordinates."""

    x: int
    y: int
    width: int
    height: int
    score: float
    class_id: int
    label: str


def _load_names(path: Path | None) -> list[str]:
    if path is None or not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def _letterbox(
    bgr: np.ndarray, size: int
) -> tuple[np.ndarray, float, tuple[float, float]]:
    """Resize with pad to square; return RGB CHW float32 0–1, ratio, (pad_w, pad_h)."""
    import cv2

    h, w = bgr.shape[:2]
    r = min(size / h, size / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    resized = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    dw, dh = (size - nw) / 2.0, (size - nh) / 2.0
    left, top = int(round(dw - 0.1)), int(round(dh - 0.1))
    canvas[top : top + nh, left : left + nw] = resized
    rgb = canvas[:, :, ::-1].astype(np.float32) / 255.0
    chw = np.transpose(rgb, (2, 0, 1))[None, ...]
    return chw, r, (dw, dh)


def _nms_xyxy(
    boxes: np.ndarray, scores: np.ndarray, iou_thresh: float
) -> list[int]:
    """Greedy NMS; boxes (N,4) xyxy."""
    if boxes.size == 0:
        return []
    order = scores.argsort()[::-1]
    keep: list[int] = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        if order.size == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        yy1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        xx2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        yy2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_r = (boxes[rest, 2] - boxes[rest, 0]) * (boxes[rest, 3] - boxes[rest, 1])
        iou = inter / (area_i + area_r - inter + 1e-6)
        order = rest[iou <= iou_thresh]
    return keep


class Yolo:
    """Engine-bound YOLO detect facade (one ORT session)."""

    def __init__(
        self,
        *,
        capture: Capture,
        window: Window,
        model_path: str | Path,
        names_path: str | Path | None = None,
        session: object | None = None,
    ) -> None:
        self._capture = capture
        self._window = window
        self._names = _load_names(Path(names_path) if names_path else None)
        self._closed = False
        if session is not None:
            self._session = session
            self._input_name = "images"
            self._input_size = 640
            return
        try:
            import onnxruntime as ort

            path = Path(model_path)
            if not path.is_file():
                raise ConstructError(f"YOLO model not found: {path}")
            self._session = ort.InferenceSession(
                str(path),
                providers=["CPUExecutionProvider"],
            )
            inp = self._session.get_inputs()[0]
            self._input_name = inp.name
            shape = inp.shape
            # [1,3,H,W] or dynamic
            h = shape[2] if len(shape) > 2 and isinstance(shape[2], int) else 640
            self._input_size = int(h) if h and h > 0 else 640
        except ConstructError:
            raise
        except Exception as exc:
            raise ConstructError(f"Failed to load YOLO model: {exc}") from exc

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._session = None
        log.info("YOLO session released")

    def _ensure_open(self) -> None:
        if self._closed:
            raise ClosedError("YOLO is closed; create a new NGE2 instance")

    def detect(
        self,
        *,
        conf: float = DEFAULT_CONF,
        iou: float = DEFAULT_IOU,
        region: tuple[int, int, int, int] | None = None,
        class_ids: list[int] | None = None,
        timeout_ms: int = 0,
        interval_ms: int = 500,
    ) -> list[Detection]:
        self._ensure_open()

        def attempt() -> list[Detection]:
            return self._detect_once(
                conf=conf, iou=iou, region=region, class_ids=class_ids
            )

        return poll_until(
            attempt,
            timeout_ms=timeout_ms,
            interval_ms=interval_ms,
            is_success=lambda dets: len(dets) > 0,
        )

    def _detect_once(
        self,
        *,
        conf: float,
        iou: float,
        region: tuple[int, int, int, int] | None,
        class_ids: list[int] | None,
    ) -> list[Detection]:
        region = validate_region(region)
        crop, off_x, off_y = grab_search(self._capture, self._window, region)
        ch, cw = crop.shape[:2]
        if ch < _MIN_SIDE or cw < _MIN_SIDE:
            log.debug("YOLO skip: crop %sx%s below min %s", cw, ch, _MIN_SIDE)
            return []

        tensor, ratio, (dw, dh) = _letterbox(crop, self._input_size)
        try:
            outs = self._session.run(None, {self._input_name: tensor})  # type: ignore[union-attr]
        except Exception as exc:
            raise FindError(f"YOLO inference failed: {exc}") from exc
        pred = np.asarray(outs[0])
        return self._postprocess(
            pred,
            conf=conf,
            iou=iou,
            class_ids=class_ids,
            ratio=ratio,
            pad=(dw, dh),
            off_x=off_x,
            off_y=off_y,
            crop_w=cw,
            crop_h=ch,
        )

    def _postprocess(
        self,
        pred: np.ndarray,
        *,
        conf: float,
        iou: float,
        class_ids: list[int] | None,
        ratio: float,
        pad: tuple[float, float],
        off_x: int,
        off_y: int,
        crop_w: int,
        crop_h: int,
    ) -> list[Detection]:
        # Accept [1, 4+nc, N] or [1, N, 4+nc]
        if pred.ndim == 3:
            pred = pred[0]
        if pred.shape[0] < pred.shape[1] and pred.shape[0] <= 512:
            # [4+nc, N] → [N, 4+nc]
            pred = pred.T
        if pred.ndim != 2 or pred.shape[1] < 5:
            log.debug("Unexpected YOLO output shape %s", pred.shape)
            return []

        boxes_xywh = pred[:, :4]
        cls_scores = pred[:, 4:]
        if cls_scores.size == 0:
            return []
        class_id = np.argmax(cls_scores, axis=1)
        scores = cls_scores[np.arange(cls_scores.shape[0]), class_id]
        mask = scores >= conf
        if class_ids is not None:
            allowed = {int(c) for c in class_ids}
            mask = mask & np.array([int(c) in allowed for c in class_id], dtype=bool)
        boxes_xywh = boxes_xywh[mask]
        scores = scores[mask]
        class_id = class_id[mask]
        if boxes_xywh.size == 0:
            return []

        # xywh center → xyxy in letterbox space
        x, y, w, h = boxes_xywh.T
        x1 = x - w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2
        boxes = np.stack([x1, y1, x2, y2], axis=1)

        dw, dh = pad
        boxes[:, [0, 2]] -= dw
        boxes[:, [1, 3]] -= dh
        boxes /= max(ratio, 1e-6)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, crop_w)
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, crop_h)

        keep = _nms_xyxy(boxes, scores, iou)
        out: list[Detection] = []
        for i in keep:
            bx1, by1, bx2, by2 = boxes[i]
            bw, bh = bx2 - bx1, by2 - by1
            if bw <= 1 or bh <= 1:
                continue
            cx = off_x + (bx1 + bx2) / 2.0
            cy = off_y + (by1 + by2) / 2.0
            mx, my = to_move_coords(self._window, cx, cy)
            cid = int(class_id[i])
            label = self._names[cid] if 0 <= cid < len(self._names) else str(cid)
            out.append(
                Detection(
                    x=mx,
                    y=my,
                    width=int(round(bw)),
                    height=int(round(bh)),
                    score=float(scores[i]),
                    class_id=cid,
                    label=label,
                )
            )
        out.sort(key=lambda d: d.score, reverse=True)
        return out


__all__ = ["DEFAULT_CONF", "DEFAULT_IOU", "Detection", "Yolo"]
