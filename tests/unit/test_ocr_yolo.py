from __future__ import annotations

import numpy as np
import pytest

from fakes import FakeCapture, FakeOcr, FakeTransport, FakeYolo, vision_factories
from nge2._engine import NGE2
from nge2._errors import ClosedError, ConstructError, FindError
from nge2._vision import validate_region
from nge2.find import Find
from nge2.ocr import Ocr, OcrLine
from nge2.window import Window
from nge2.yolo import Detection, Yolo


def test_engine_facades(tmp_path):
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )
    try:
        assert isinstance(engine.find, Find)
        assert isinstance(engine.ocr, FakeOcr)
        assert isinstance(engine.yolo, FakeYolo)
    finally:
        engine.close()


def test_missing_yolo_construct_error(tmp_path):
    with pytest.raises(ConstructError, match="YOLO model"):
        NGE2(
            resource_dir=tmp_path,
            capture_factory=lambda b: FakeCapture(b),
            transport_factory=lambda: FakeTransport(),
            log_dir=tmp_path / "logs",
            ocr_factory=lambda **k: FakeOcr(**k),
        )


def test_yolo_detect_fake_and_order(tmp_path):
    dets = [
        Detection(x=1, y=1, width=10, height=10, score=0.4, class_id=0, label="a"),
        Detection(x=2, y=2, width=10, height=10, score=0.9, class_id=1, label="b"),
    ]
    yolo = FakeYolo(detections=dets)
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        ocr_factory=lambda **k: FakeOcr(**k),
        yolo_factory=lambda **k: yolo,
    )
    try:
        hits = engine.yolo.detect(conf=0.5)
        assert len(hits) == 1 and hits[0].label == "b"
        assert yolo.detect_calls == 1
    finally:
        engine.close()


def test_ocr_recognize_fake(tmp_path):
    lines = [
        OcrLine(text="hi", score=0.5, x=1, y=2, box=(0, 0, 10, 10)),
        OcrLine(text="yo", score=0.9, x=3, y=4, box=(1, 1, 11, 11)),
    ]
    ocr = FakeOcr(lines=lines)
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        ocr_factory=lambda **k: ocr,
        yolo_factory=lambda **k: FakeYolo(**k),
    )
    try:
        got = engine.ocr.recognize()
        assert got == lines
        assert ocr.recognize_calls == 1
    finally:
        engine.close()


def test_invalid_region_raises():
    with pytest.raises(FindError):
        validate_region((10, 10, 5, 20))


def test_undersized_crop_returns_empty():
    class Eng:
        def __call__(self, *_a, **_k):
            raise AssertionError("should not run")

    cap = FakeCapture(frame=np.zeros((10, 10, 3), dtype=np.uint8))
    ocr = Ocr(capture=cap, window=Window(None), engine=Eng())
    assert ocr.recognize() == []

    class Sess:
        def run(self, *a, **k):
            raise AssertionError("should not run")

        def get_inputs(self):
            return []

    yolo = Yolo(
        capture=cap,
        window=Window(None),
        model_path="x.onnx",
        session=Sess(),
    )
    # 10x10 < YOLO min 32
    assert yolo.detect() == []


def test_ocr_maps_rapidocr_raw():
    class Eng:
        def __call__(self, image):
            h, w = image.shape[:2]
            box = [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]]
            return [(box, "Hello", 0.91)], None

    cap = FakeCapture(frame=np.zeros((40, 80, 3), dtype=np.uint8))
    ocr = Ocr(capture=cap, window=Window(None), engine=Eng())
    lines = ocr.recognize()
    assert len(lines) == 1
    assert lines[0].text == "Hello"
    assert lines[0].score == pytest.approx(0.91)
    assert lines[0].box == (0, 0, 79, 39)
    assert (lines[0].x, lines[0].y) == (40, 20)


def test_close_releases_ocr_yolo(tmp_path):
    ocr = FakeOcr()
    yolo = FakeYolo()
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        ocr_factory=lambda **k: ocr,
        yolo_factory=lambda **k: yolo,
    )
    engine.close()
    assert ocr.closed == 1
    assert yolo.closed == 1
    with pytest.raises(ClosedError):
        ocr.recognize()
    with pytest.raises(ClosedError):
        yolo.detect()
    engine.close()
    assert ocr.closed == 1
    assert yolo.closed == 1


def test_ocr_yolo_close_clears_runtime():
    class Eng:
        def __call__(self, *_a, **_k):
            raise AssertionError("should not run after close")

    class Sess:
        def run(self, *a, **k):
            raise AssertionError("should not run after close")

        def get_inputs(self):
            class I:
                name = "x"
                shape = (1, 3, 32, 32)

            return [I()]

    cap = FakeCapture(frame=np.zeros((64, 64, 3), dtype=np.uint8))
    ocr = Ocr(capture=cap, window=Window(None), engine=Eng())
    yolo = Yolo(
        capture=cap,
        window=Window(None),
        model_path="x.onnx",
        session=Sess(),
    )
    ocr.close()
    yolo.close()
    with pytest.raises(ClosedError):
        ocr.recognize()
    with pytest.raises(ClosedError):
        yolo.detect()
