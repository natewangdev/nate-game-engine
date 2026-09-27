from __future__ import annotations

import pytest

from fakes import FakeCapture, FakeTransport
from nge2._engine import NGE2
from nge2._errors import ConstructError, ControlError


def _eng(tmp_path, transport: FakeTransport, humanize=True):
    return NGE2(
        resource_dir=tmp_path,
        humanize=humanize,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: transport,
        enable_file_logging=False,
    )


def test_move_humanize_and_instant(tmp_path):
    t = FakeTransport("C1")
    eng = _eng(tmp_path, t, humanize=True)
    eng.control.move(10, 10, duration=0.02, spread=0)
    assert any(c.startswith("MA ") for c in t.commands)
    eng.close()

    t2 = FakeTransport("C2")
    eng2 = _eng(tmp_path, t2, humanize=False)
    before = len(t2.commands)
    eng2.control.move(50, 60, duration=1.0, spread=20)
    ma = [c for c in t2.commands[before:] if c.startswith("MA ")]
    assert len(ma) == 1
    eng2.close()


def test_clicks_and_keys(tmp_path):
    t = FakeTransport("C3")
    eng = _eng(tmp_path, t, humanize=False)
    eng.control.left_click(hold=0.05)
    eng.control.right_click(hold=0.05)
    eng.control.left_down()
    eng.control.left_up()
    eng.control.right_down()
    eng.control.right_up()
    eng.control.move_and_click(1, 2, hold=0.05)
    eng.control.key_down("a")
    eng.control.key_up("a")
    eng.control.key_click("b")
    eng.control.key_click("ctrl", "c")
    joined = "\n".join(t.commands)
    assert "CLK L" in joined and "CLK R" in joined
    assert "BTN L 1" in joined and "BTN L 0" in joined
    assert "BTN R 1" in joined and "BTN R 0" in joined
    assert "KD " in joined and "KU " in joined and "KP " in joined
    assert "MOD " in joined
    eng.close()


def test_unknown_key_before_send(tmp_path):
    t = FakeTransport("C4")
    eng = _eng(tmp_path, t)
    before = list(t.commands)
    with pytest.raises(ControlError, match="Unknown key"):
        eng.control.key_down("not-real-key")
    assert t.commands == before
    eng.close()


def test_port_busy(tmp_path):
    t1 = FakeTransport("BUSY1")
    e1 = _eng(tmp_path, t1)
    with pytest.raises(ConstructError, match="busy"):
        _eng(tmp_path, FakeTransport("BUSY1"))
    e1.close()
