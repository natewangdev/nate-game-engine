from __future__ import annotations

import pytest

from fakes import FakeCapture, FakeTransport, vision_factories
from nge2._engine import NGE2
from nge2._errors import ControlError


def _eng(tmp_path, transport: FakeTransport, humanize=True):
    return NGE2(
        resource_dir=tmp_path,
        humanize=humanize,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: transport,
        log_dir=tmp_path / "logs",
        **vision_factories(),
    )


def test_drag_left_and_right(tmp_path):
    t = FakeTransport("G1")
    eng = _eng(tmp_path, t, humanize=False)
    before = len(t.commands)
    eng.control.drag(10, 20, 30, 40)
    seq = t.commands[before:]
    assert seq[0].startswith("MA ")
    assert seq[1] == "BTN L 1"
    assert seq[2].startswith("MA ")
    assert seq[3] == "BTN L 0"

    before = len(t.commands)
    eng.control.drag(1, 2, 3, 4, button="R")
    seq = t.commands[before:]
    assert seq[1] == "BTN R 1" and seq[3] == "BTN R 0"
    eng.close()


def test_scroll_up_down_clamp_and_invalid(tmp_path):
    t = FakeTransport("G2")
    eng = _eng(tmp_path, t, humanize=False)
    eng.control.scroll("up", 3)
    eng.control.scroll("down", 5)
    eng.control.scroll("up", 200)
    assert "WHEEL 3" in t.commands
    assert "WHEEL -5" in t.commands
    assert "WHEEL 127" in t.commands

    before = list(t.commands)
    with pytest.raises(ControlError, match="notches"):
        eng.control.scroll("up", 0)
    with pytest.raises(ControlError, match="direction"):
        eng.control.scroll("left", 1)
    assert t.commands == before
    eng.close()


def test_double_click(tmp_path):
    t = FakeTransport("G3")
    eng = _eng(tmp_path, t, humanize=False)
    eng.control.double_click(hold=0.05, interval=0.01)
    clk = [c for c in t.commands if c.startswith("CLK L")]
    assert len(clk) == 2

    before = list(t.commands)
    with pytest.raises(ControlError, match="both x and y"):
        eng.control.double_click(x=1)
    assert t.commands == before

    before_n = len(t.commands)
    eng.control.double_click(5, 6, hold=0.05, interval=0.01)
    after = t.commands[before_n:]
    ma = [c for c in after if c.startswith("MA ")]
    assert len(ma) == 1  # exact pre-move only; no scatter path extras under humanize=False
    assert len([c for c in after if c.startswith("CLK L")]) == 2
    eng.close()


def test_double_click_exact_under_humanize(tmp_path):
    t = FakeTransport("G3b")
    eng = _eng(tmp_path, t, humanize=True)
    eng.control.double_click(100, 200, hold=0.05, interval=0.01, duration=0.02)
    ma = [c for c in t.commands if c.startswith("MA ")]
    assert ma  # path may have multiple waypoints but final equals exact target mapping
    # Last MA before first CLK should be the exact device coords for (100,200)
    clk_i = next(i for i, c in enumerate(t.commands) if c.startswith("CLK L"))
    last_ma = [c for c in t.commands[:clk_i] if c.startswith("MA ")][-1]
    # Recompute expected device coords via a second engine of same screen size
    w, h = eng.control.screen_size
    from nge2.control import HID_MAX

    ex = int(round(100 * HID_MAX / max(1, w - 1)))
    ey = int(round(200 * HID_MAX / max(1, h - 1)))
    assert last_ma == f"MA {ex} {ey}"
    eng.close()


def test_hotkey_matches_key_click(tmp_path):
    t1 = FakeTransport("G4a")
    e1 = _eng(tmp_path, t1, humanize=False)
    e1.control.key_click("ctrl", "c", hold=0.05)
    cmds1 = [c for c in t1.commands if c.startswith(("MOD ", "KP "))]
    e1.close()

    t2 = FakeTransport("G4b")
    e2 = _eng(tmp_path, t2, humanize=False)
    e2.control.hotkey("ctrl", "c", hold=0.05)
    cmds2 = [c for c in t2.commands if c.startswith(("MOD ", "KP "))]
    e2.close()

    assert cmds1 == cmds2
    assert any(c.startswith("MOD ") for c in cmds1)
    assert any(c.startswith("KP ") for c in cmds1)
