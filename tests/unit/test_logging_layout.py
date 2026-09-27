from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from fakes import FakeCapture, FakeTransport, vision_factories
from nge2._engine import NGE2
from nge2.log import (
    allocate_log_file,
    get_logger,
    next_nge_log_index,
    resolve_log_dir,
)


def _eng(tmp_path, port: str = "LOG1", **kwargs):
    return NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(port=port),
        log_dir=tmp_path / "logs",
        **vision_factories(),
        **kwargs,
    )


def test_resolve_default_log_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert resolve_log_dir(None) == (tmp_path / "logs").resolve()


def test_allocate_index_and_padding(tmp_path):
    day = tmp_path / "2026-09-27"
    day.mkdir(parents=True)
    (day / "nge-001.log").write_text("a", encoding="utf-8")
    (day / "nge-002.log").write_text("b", encoding="utf-8")
    assert next_nge_log_index(day) == 3
    path = allocate_log_file(tmp_path, when=datetime(2026, 9, 27, 12, 0, 0))
    assert path.name == "nge-003.log"
    assert path.parent.name == "2026-09-27"


def test_engine_creates_log_without_module_name(tmp_path):
    eng = _eng(tmp_path, port="LOGA")
    get_logger("capture").info("hello-layout")
    assert eng._log_path is not None
    text = eng._log_path.read_text(encoding="utf-8")
    assert "hello-layout" in text
    assert "nge.capture" not in text
    assert "nge.engine" not in text
    eng.close()


def test_two_engines_increment_log_index(tmp_path):
    e1 = _eng(tmp_path, port="LOGB1")
    e2 = _eng(tmp_path, port="LOGB2")
    assert e1._log_path is not None and e2._log_path is not None
    assert e1._log_path.name == "nge-001.log"
    assert e2._log_path.name == "nge-002.log"
    e1.close()
    e2.close()


def test_error_screenshot_jpg(tmp_path):
    eng = _eng(tmp_path, port="LOGC")
    get_logger("demo").error("失败原因")
    shot_dir = eng._log_path.parent / "screenshot"  # type: ignore[union-attr]
    jpgs = list(shot_dir.glob("*.jpg"))
    assert len(jpgs) == 1
    assert jpgs[0].stat().st_size > 0
    eng.close()


def test_info_no_screenshot(tmp_path):
    eng = _eng(tmp_path, port="LOGD")
    get_logger("demo").info("no-shot")
    shot_dir = eng._log_path.parent / "screenshot"  # type: ignore[union-attr]
    assert not shot_dir.exists() or list(shot_dir.glob("*.jpg")) == []
    eng.close()


def test_screenshot_soft_fail(tmp_path):
    class BoomCapture(FakeCapture):
        def grab(self, region=None):
            raise RuntimeError("boom")

    eng = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: BoomCapture(b),
        transport_factory=lambda: FakeTransport(port="LOGE"),
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )
    get_logger("demo").error("still-ok")
    # Must not raise; log file should still contain the error line
    text = eng._log_path.read_text(encoding="utf-8")  # type: ignore[union-attr]
    assert "still-ok" in text
    eng.close()
