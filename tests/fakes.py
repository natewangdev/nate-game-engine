"""Test doubles for nge2 (no hardware)."""

from __future__ import annotations

import numpy as np


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


def failing_capture_factory(backend: str):
    from nge2._errors import CaptureError

    raise CaptureError(f"Capture backend {backend!r} is unavailable: fake")
