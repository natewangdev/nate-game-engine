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
        self.recognize_calls = 0
        self.closed = 0

    def close(self) -> None:
        if self.closed:
            return
        self.closed += 1

    def recognize(self, *, region=None) -> list[OcrLine]:
        if self.closed:
            from nge2._errors import ClosedError

            raise ClosedError("OCR is closed; create a new NGE2 instance")
        self.recognize_calls += 1
        return list(self.lines)


class FakeYolo:
    def __init__(
        self, *args, detections: list[Detection] | None = None, **kwargs
    ) -> None:
        self.detections = list(detections or [])
        self.detect_calls = 0
        self.closed = 0

    def close(self) -> None:
        if self.closed:
            return
        self.closed += 1

    def detect(self, **kwargs) -> list[Detection]:
        if self.closed:
            from nge2._errors import ClosedError

            raise ClosedError("YOLO is closed; create a new NGE2 instance")
        self.detect_calls += 1
        conf = float(kwargs.get("conf", 0.25))
        hits = [d for d in self.detections if d.score >= conf]
        hits.sort(key=lambda d: d.score, reverse=True)
        return hits


def vision_factories(**kwargs):
    """Default test hooks so NGE2 construct does not need ONNX files."""
    return {
        "ocr_factory": kwargs.get("ocr_factory", lambda **k: FakeOcr(**k)),
        "yolo_factory": kwargs.get("yolo_factory", lambda **k: FakeYolo(**k)),
    }


def failing_capture_factory(backend: str):
    from nge2._errors import CaptureError

    raise CaptureError(f"Capture backend {backend!r} is unavailable: fake")
