"""Unit tests for nge2.time sleep / delay."""

from __future__ import annotations

import pytest

import nge2.time as time_mod
from nge2._engine import NGE2
from nge2.time import Time, delay, sleep
from tests.fakes import FakeCapture, FakeTransport, vision_factories


def test_fixed_sleep_returns_ms(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[float] = []
    monkeypatch.setattr(time_mod, "_sleep", lambda s: seen.append(s))
    assert sleep(250) == 250
    assert seen == [0.25]
    assert Time.sleep(0) == 0
    assert seen == [0.25]  # zero: no sleep call


def test_random_closed_interval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time_mod, "_sleep", lambda s: None)
    monkeypatch.setattr(time_mod, "_randint", lambda a, b: a)
    assert sleep(10, 30) == 10
    monkeypatch.setattr(time_mod, "_randint", lambda a, b: b)
    assert sleep(10, 30) == 30
    monkeypatch.setattr(time_mod, "_randint", lambda a, b: (a + b) // 2)
    assert sleep(10, 30) == 20


def test_min_equals_max(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time_mod, "_sleep", lambda s: None)
    calls: list[tuple[int, int]] = []

    def fake_randint(a: int, b: int) -> int:
        calls.append((a, b))
        return a

    monkeypatch.setattr(time_mod, "_randint", fake_randint)
    assert sleep(7, 7) == 7
    assert calls == [(7, 7)]


def test_delay_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time_mod, "_sleep", lambda s: None)
    assert delay is sleep
    assert delay(3) == 3
    assert Time.delay(1, 1) == 1


def test_three_surfaces(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time_mod, "_sleep", lambda s: None)
    monkeypatch.setattr(time_mod, "_randint", lambda a, b: 42)
    engine = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(),
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )
    try:
        assert sleep(5) == 5
        assert Time.sleep(5) == 5
        assert engine.time.sleep(5) == 5
        assert sleep(1, 100) == 42
        assert Time.sleep(1, 100) == 42
        assert engine.time.sleep(1, 100) == 42
        assert engine.time.delay(9) == 9
    finally:
        engine.close()
        # Still usable after close (facade + import)
        assert engine.time.sleep(0) == 0
        assert sleep(0) == 0


def test_illegal_args() -> None:
    with pytest.raises(ValueError, match="1 argument|2 arguments"):
        sleep()  # type: ignore[call-arg]
    with pytest.raises(ValueError, match="1 argument|2 arguments"):
        sleep(1, 2, 3)  # type: ignore[call-arg]
    with pytest.raises(ValueError, match=">= 0"):
        sleep(-1)
    with pytest.raises(ValueError, match="min_ms"):
        sleep(10, 5)
    with pytest.raises(ValueError, match="non-negative int"):
        sleep(1.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="non-negative int"):
        sleep(True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="non-negative int"):
        sleep("10")  # type: ignore[arg-type]
