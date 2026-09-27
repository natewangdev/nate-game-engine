from __future__ import annotations

import pytest

from fakes import FakeCapture, FakeTransport, FakeOcr, FakeYolo, vision_factories
from nge2._engine import NGE2
from nge2._errors import ConstructError
from nge2.find import Find


def test_engine_vision_facades(tmp_path):
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


def test_mode_0_1_rejected(tmp_path):
    for mode in (0, 1):
        with pytest.raises(ConstructError, match="not implemented"):
            NGE2(
                resource_dir=tmp_path,
                control_mode=mode,
                capture_factory=lambda b: FakeCapture(b),
                transport_factory=lambda: FakeTransport(),
                log_dir=tmp_path / "logs",
                **vision_factories(),
            )
