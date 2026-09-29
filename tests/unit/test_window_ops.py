"""Unit tests for window find / activate / topmost / move (faked Win32)."""

from __future__ import annotations

import pytest

from nge2._errors import WindowError
from nge2.window import Window, WindowMatch
import nge2.window as window_mod


def _matches() -> list[WindowMatch]:
    return [
        WindowMatch(hwnd=101, title="Notepad - demo.txt", rect=(10, 20, 410, 320)),
        WindowMatch(hwnd=102, title="Chrome", rect=(0, 0, 800, 600)),
        WindowMatch(hwnd=103, title="NOTEPAD++", rect=(50, 50, 250, 250)),
    ]


def test_find_by_title_case_insensitive_substring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(window_mod, "_list_visible_toplevel", _matches)
    w = Window(None)
    hits = w.find_by_title("note")
    assert [m.hwnd for m in hits] == [101, 103]
    assert hits[0].title.startswith("Notepad")
    assert hits[0].rect == (10, 20, 410, 320)


def test_find_by_title_empty_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(window_mod, "_list_visible_toplevel", _matches)
    assert Window(None).find_by_title("zzz-missing") == []


def test_find_by_title_blank_raises() -> None:
    w = Window(None)
    with pytest.raises(WindowError, match="non-blank"):
        w.find_by_title("   ")
    with pytest.raises(WindowError, match="non-blank"):
        w.find_by_title("")


def test_find_does_not_rebind(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(window_mod, "_list_visible_toplevel", _matches)
    w = Window(999)
    w.find_by_title("Chrome")
    assert w.hwnd == 999


def test_activate_uses_bound_hwnd(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[int] = []

    def fake(hwnd: int) -> None:
        seen.append(hwnd)

    monkeypatch.setattr(window_mod, "_activate_hwnd", fake)
    Window(42).activate()
    assert seen == [42]


def test_activate_explicit_hwnd_no_rebind(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[int] = []
    monkeypatch.setattr(window_mod, "_activate_hwnd", lambda h: seen.append(h))
    w = Window(1)
    w.activate(hwnd=202)
    assert seen == [202]
    assert w.hwnd == 1


def test_activate_missing_target() -> None:
    with pytest.raises(WindowError, match="No window hwnd"):
        Window(None).activate()


def test_set_topmost(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[int, bool]] = []

    def fake(hwnd: int, enabled: bool) -> None:
        calls.append((hwnd, enabled))

    monkeypatch.setattr(window_mod, "_set_topmost_hwnd", fake)
    w = Window(7)
    w.set_topmost(True)
    w.set_topmost(False, hwnd=8)
    assert calls == [(7, True), (8, False)]
    assert w.hwnd == 7


def test_set_topmost_missing_target() -> None:
    with pytest.raises(WindowError, match="No window hwnd"):
        Window(None).set_topmost(True)


def test_move_screen_coords(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[int, int, int]] = []

    def fake(hwnd: int, x: int, y: int) -> None:
        calls.append((hwnd, x, y))

    monkeypatch.setattr(window_mod, "_move_hwnd", fake)
    w = Window(5)
    w.move(100, 200)
    w.move(1, 2, hwnd=9)
    assert calls == [(5, 100, 200), (9, 1, 2)]
    assert w.hwnd == 5


def test_move_missing_target() -> None:
    with pytest.raises(WindowError, match="No window hwnd"):
        Window(None).move(0, 0)


def test_activate_propagates_helper_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(_hwnd: int) -> None:
        raise WindowError("SetForegroundWindow failed")

    monkeypatch.setattr(window_mod, "_activate_hwnd", boom)
    with pytest.raises(WindowError, match="SetForegroundWindow"):
        Window(1).activate()
