"""Test doubles for nge2 (no hardware)."""

from __future__ import annotations

import numpy as np

from nge2.ocr import OcrLine
from nge2.yolo import Detection


class FakeCapture:
    def __init__(
        self,
        backend: str = "dxcam",
        frame: np.ndarray | None = None,
    ) -> None:
        self.backend_name = backend
        self._active = True
        self.released = 0
        self.grabs = 0
        self.frame = frame

    def grab(self, region=None):
        if not self._active:
            self._active = True
        self.grabs += 1
        if self.frame is not None:
            frame = self.frame
            if region:
                l, t, r, b = (int(v) for v in region)
                return frame[t:b, l:r].copy()
            return frame.copy()
        if region:
            l, t, r, b = region
            h, w = max(1, b - t), max(1, r - l)
        else:
            h, w = 1080, 1920
        return np.zeros((h, w, 3), dtype=np.uint8)

    def release(self) -> None:
        self._active = False
        self.released += 1


class FakeTransport:
    def __init__(self, port: str = "FAKECOM1") -> None:
        self.port = port
        self.commands: list[str] = []
        self._open = False

    def open(self) -> FakeTransport:
        self._open = True
        return self

    def close(self) -> None:
        self._open = False

    def command(self, line: str, expect: str = "OK") -> str:
        self.commands.append(line)
        if line.strip() == "PING":
            return "PONG"
        if expect == "PONG":
            return "PONG"
        return "OK"

    def ping(self) -> bool:
        return self.command("PING", expect="PONG") == "PONG"


class FakeOcr:
    def __init__(self, *args, lines: list[OcrLine] | None = None, **kwargs) -> None:
        self.lines = list(lines or [])
        self.line_queue: list[list[OcrLine]] | None = None
        self.recognize_calls = 0
        self.closed = 0

    def close(self) -> None:
        if self.closed:
            return
        self.closed += 1

    def recognize(self, *, region=None, min_score: float = 0.0) -> list[OcrLine]:
        if self.closed:
            from nge2._errors import ClosedError

            raise ClosedError("OCR is closed; create a new NGE2 instance")
        self.recognize_calls += 1
        if self.line_queue is not None and self.line_queue:
            self.lines = list(self.line_queue.pop(0))
        return [ln for ln in self.lines if ln.score >= min_score]

    def find_text(
        self,
        text: str,
        *,
        region=None,
        multi: bool = False,
        timeout_ms: int = 0,
        interval_ms: int = 1000,
        min_score: float = 0.0,
    ):
        from nge2._errors import FindError
        from nge2._vision import poll_until

        if self.closed:
            from nge2._errors import ClosedError

            raise ClosedError("OCR is closed; create a new NGE2 instance")
        if not isinstance(text, str) or not text.strip():
            raise FindError("find_text query must be a non-blank string")
        needle = text.casefold()

        def attempt():
            lines = self.recognize(region=region, min_score=min_score)
            matched = [ln for ln in lines if needle in ln.text.casefold()]
            if multi:
                return matched
            return matched[0] if matched else None

        return poll_until(
            attempt,
            timeout_ms=timeout_ms,
            interval_ms=interval_ms,
            is_success=lambda r: (len(r) > 0) if multi else (r is not None),
        )


class FakeYolo:
    def __init__(
        self, *args, detections: list[Detection] | None = None, **kwargs
    ) -> None:
        self.detections = list(detections or [])
        self.detect_queue: list[list[Detection]] | None = None
        self.detect_calls = 0
        self.closed = 0

    def close(self) -> None:
        if self.closed:
            return
        self.closed += 1

    def detect(self, **kwargs) -> list[Detection]:
        from nge2._vision import poll_until

        if self.closed:
            from nge2._errors import ClosedError

            raise ClosedError("YOLO is closed; create a new NGE2 instance")
        conf = float(kwargs.get("conf", 0.25))
        timeout_ms = int(kwargs.get("timeout_ms", 0))
        interval_ms = int(kwargs.get("interval_ms", 500))

        def attempt() -> list[Detection]:
            self.detect_calls += 1
            if self.detect_queue is not None and self.detect_queue:
                self.detections = list(self.detect_queue.pop(0))
            hits = [d for d in self.detections if d.score >= conf]
            hits.sort(key=lambda d: d.score, reverse=True)
            return hits

        return poll_until(
            attempt,
            timeout_ms=timeout_ms,
            interval_ms=interval_ms,
            is_success=lambda dets: len(dets) > 0,
        )

def vision_factories(**kwargs):
    """Default test hooks so NGE2 construct does not need ONNX files."""
    return {
        "ocr_factory": kwargs.get("ocr_factory", lambda **k: FakeOcr(**k)),
        "yolo_factory": kwargs.get("yolo_factory", lambda **k: FakeYolo(**k)),
    }


def failing_capture_factory(backend: str):
    from nge2._errors import CaptureError

    raise CaptureError(f"Capture backend {backend!r} is unavailable: fake")
