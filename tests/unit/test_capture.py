from __future__ import annotations

import numpy as np
import pytest

from fakes import FakeCapture, FakeTransport, failing_capture_factory, vision_factories
from nge2._engine import NGE2
from nge2._errors import ClosedError, ConstructError


def _engine(tmp_path, port="FAKE1", capture_factory=None):
    return NGE2(
        resource_dir=tmp_path,
        capture="dxcam",
        capture_factory=capture_factory or (lambda b: FakeCapture(b)),
        transport_factory=lambda: FakeTransport(port=port),
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )


def test_grab_full_and_region(tmp_path):
    eng = _engine(tmp_path)
    frame = eng.capture.grab()
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8
    crop = eng.capture.grab(region=(10, 20, 110, 70))
    assert crop.shape == (50, 100, 3)
    eng.close()


def test_release_then_grab_recreates(tmp_path):
    cap = FakeCapture("dxcam")
    eng = _engine(tmp_path, capture_factory=lambda b: cap)
    eng.capture.release()
    assert cap.released == 1
    frame = eng.capture.grab()
    assert frame.ndim == 3
    assert cap._active is True
    eng.close()


def test_backend_unavailable(tmp_path):
    with pytest.raises(ConstructError, match="unavailable"):
        NGE2(
            resource_dir=tmp_path,
            capture_factory=failing_capture_factory,
            transport_factory=lambda: FakeTransport(),
            log_dir=tmp_path / "logs",
            **vision_factories(),
        )


def test_instances_independent_capture(tmp_path):
    a = FakeCapture("dxcam")
    b = FakeCapture("mss")
    e1 = _engine(tmp_path, port="P1", capture_factory=lambda _: a)
    e2 = _engine(tmp_path, port="P2", capture_factory=lambda _: b)
    e1.capture.grab()
    e2.capture.grab()
    assert a.grabs == 1 and b.grabs == 1
    e1.close()
    e2.close()


def test_closed_capture_raises(tmp_path):
    eng = _engine(tmp_path)
    eng.close()
    with pytest.raises(ClosedError):
        _ = eng.capture
