"""Unit tests for vision wait/poll (find_text, find_image timeout, detect timeout)."""

from __future__ import annotations

import numpy as np
import pytest

import nge2._vision as vision
from fakes import FakeCapture, FakeOcr, FakeTransport, FakeYolo, vision_factories
from nge2._engine import NGE2
from nge2._errors import FindError
from nge2._vision import poll_until, validate_wait
from nge2.find import Match
from nge2.ocr import OcrLine
from nge2.yolo import Detection


def test_validate_wait_ok_and_errors():
    validate_wait(0, 500)
    validate_wait(1000, 500)
    validate_wait(500, 500)
    with pytest.raises(FindError, match=">="):
        validate_wait(100, 500)
    with pytest.raises(FindError, match="interval_ms"):
        validate_wait(1000, 0)
    with pytest.raises(FindError, match=">="):
        validate_wait(-1, 100)


def test_poll_until_once_and_early_success(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    clock = {"t": 0.0}

    monkeypatch.setattr(vision, "_sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(vision, "_monotonic", lambda: clock["t"])

    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        return calls["n"]

    assert poll_until(attempt, timeout_ms=0, interval_ms=500, is_success=lambda v: v > 0) == 1
    assert calls["n"] == 1
    assert sleeps == []

    calls["n"] = 0

    def attempt2():
        calls["n"] += 1
        clock["t"] += 0.05
        return calls["n"] if calls["n"] >= 2 else 0

    assert (
        poll_until(attempt2, timeout_ms=1000, interval_ms=100, is_success=lambda v: v > 0)
        == 2
    )
    assert calls["n"] == 2
    assert sleeps  # slept between attempts


def test_poll_until_timeout_returns_last(monkeypatch: pytest.MonkeyPatch):
    clock = {"t": 0.0}
    monkeypatch.setattr(vision, "_sleep", lambda s: clock.__setitem__("t", clock["t"] + s))
    monkeypatch.setattr(vision, "_monotonic", lambda: clock["t"])

    def attempt():
        return None

    assert (
        poll_until(attempt, timeout_ms=200, interval_ms=100, is_success=lambda v: v is not None)
        is None
    )


def _engine(tmp_path, **kwargs):
    return NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        **vision_factories(**kwargs),
    )


def test_find_text_substring_multi_and_blank(tmp_path):
    lines = [
        OcrLine(text="开始组队", score=0.8, x=10, y=20, box=(0, 0, 20, 40)),
        OcrLine(text="取消", score=0.9, x=1, y=2, box=(0, 0, 1, 1)),
        OcrLine(text="组队大厅", score=0.7, x=30, y=40, box=(1, 1, 2, 2)),
    ]
    ocr = FakeOcr(lines=lines)
    engine = _engine(tmp_path, ocr_factory=lambda **k: ocr)
    try:
        hit = engine.ocr.find_text("组队")
        assert isinstance(hit, OcrLine)
        assert hit.text == "开始组队"  # higher score first among matches
        multi = engine.ocr.find_text("组队", multi=True)
        assert [m.text for m in multi] == ["开始组队", "组队大厅"]
        assert engine.ocr.find_text("没有") is None
        assert engine.ocr.find_text("没有", multi=True) == []
        with pytest.raises(FindError, match="non-blank"):
            engine.ocr.find_text("  ")
    finally:
        engine.close()


def test_find_text_poll_early(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(vision, "_sleep", lambda s: None)
    clock = {"t": 0.0}
    monkeypatch.setattr(vision, "_monotonic", lambda: clock["t"])

    empty: list[OcrLine] = []
    hit = [OcrLine(text="组队", score=0.9, x=1, y=2, box=(0, 0, 1, 1))]
    ocr = FakeOcr(lines=empty)
    ocr.line_queue = [empty, hit]
    engine = _engine(tmp_path, ocr_factory=lambda **k: ocr)
    try:
        got = engine.ocr.find_text("组队", timeout_ms=2000, interval_ms=100)
        assert got is not None and got.text == "组队"
        assert ocr.recognize_calls == 2
    finally:
        engine.close()


def test_find_image_timeout_miss_and_illegal(tmp_path, monkeypatch: pytest.MonkeyPatch):
    import cv2

    monkeypatch.setattr(vision, "_sleep", lambda s: None)
    clock = {"t": 0.0}

    def advance_monotonic():
        # Each call advances so deadline is eventually hit after a few attempts.
        clock["t"] += 0.15
        return clock["t"]

    monkeypatch.setattr(vision, "_monotonic", advance_monotonic)

    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    other = np.zeros((12, 12, 3), dtype=np.uint8)
    other[0:6, 0:6] = (0, 0, 255)
    ok, buf = cv2.imencode(".png", other)
    assert ok
    (tmp_path / "other.png").write_bytes(buf.tobytes())

    cap = FakeCapture(frame=frame)
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: cap,
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )
    try:
        assert engine.find.find_image("other.png", threshold=0.8, timeout_ms=300, interval_ms=100) is None
        assert cap.grabs >= 2
        with pytest.raises(FindError):
            engine.find.find_image("other.png", timeout_ms=100, interval_ms=500)
    finally:
        engine.close()


def test_find_image_timeout_hit(tmp_path, monkeypatch: pytest.MonkeyPatch):
    import cv2

    monkeypatch.setattr(vision, "_sleep", lambda s: None)
    clock = {"t": 0.0}
    monkeypatch.setattr(vision, "_monotonic", lambda: clock["t"])

    blank = np.zeros((100, 120, 3), dtype=np.uint8)
    tmpl = np.random.randint(40, 220, (20, 30, 3), dtype=np.uint8)
    framed = blank.copy()
    framed[40:60, 50:80] = tmpl
    ok, buf = cv2.imencode(".png", tmpl)
    assert ok
    (tmp_path / "btn.png").write_bytes(buf.tobytes())

    frames = [blank.copy(), framed.copy()]
    grab_i = {"i": 0}

    class SeqCapture(FakeCapture):
        def grab(self, region=None):
            self.grabs += 1
            idx = min(grab_i["i"], len(frames) - 1)
            grab_i["i"] += 1
            return frames[idx]
    cap = SeqCapture(frame=blank)
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: cap,
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )
    try:
        m = engine.find.find_image("btn.png", timeout_ms=2000, interval_ms=100)
        assert isinstance(m, Match)
        assert cap.grabs == 2
    finally:
        engine.close()


def test_yolo_detect_poll(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(vision, "_sleep", lambda s: None)
    clock = {"t": 0.0}
    monkeypatch.setattr(vision, "_monotonic", lambda: clock["t"])

    det = Detection(x=1, y=2, width=10, height=10, score=0.9, class_id=0, label="a")
    yolo = FakeYolo(detections=[])
    yolo.detect_queue = [[], [det]]
    engine = _engine(tmp_path, yolo_factory=lambda **k: yolo)
    try:
        hits = engine.yolo.detect(timeout_ms=2000, interval_ms=100)
        assert len(hits) == 1 and hits[0].label == "a"
        assert yolo.detect_calls == 2
    finally:
        engine.close()

    yolo2 = FakeYolo(detections=[])
    engine2 = _engine(tmp_path, yolo_factory=lambda **k: yolo2)
    try:
        clock["t"] = 0.0

        def mono():
            clock["t"] += 0.2
            return clock["t"]

        monkeypatch.setattr(vision, "_monotonic", mono)
        assert engine2.yolo.detect(timeout_ms=300, interval_ms=100) == []
    finally:
        engine2.close()
