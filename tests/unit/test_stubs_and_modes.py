from __future__ import annotations

import pytest

from fakes import FakeCapture, FakeTransport
from nge2 import ocr, yolo
from nge2._engine import NGE2
from nge2._errors import ConstructError
from nge2.find import Find


def test_ocr_yolo_stubs_raise():
    with pytest.raises(NotImplementedError):
        ocr.recognize(0, 0, 1, 1)
    with pytest.raises(NotImplementedError):
        yolo.detect("m.onnx", 0, 0, 1, 1)


def test_engine_find_is_facade(tmp_path):
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
    )
    try:
        assert isinstance(engine.find, Find)
    finally:
        engine.close()


def test_mode_0_1_rejected(tmp_path):
    for mode in (0, 1):
        with pytest.raises(ConstructError, match="not implemented"):
            NGE2(
                resource_dir=tmp_path,
                control_mode=mode,
                capture_factory=lambda b: FakeCapture(b),
                transport_factory=lambda: FakeTransport(),
                log_dir=tmp_path / "logs",
            )
