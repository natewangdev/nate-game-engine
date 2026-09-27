from __future__ import annotations

from nge2.window import ClientRegion, Window


def test_no_hwnd_passthrough():
    w = Window(None)
    assert w.hwnd is None
    assert w.title == ""
    assert w.client_region is None
    assert w.client_to_screen(10, 20) == (10, 20)
    assert w.screen_to_client(10, 20) == (10, 20)


def test_client_region_dataclass():
    r = ClientRegion(local=(0, 0, 100, 50), screen=(10, 20, 110, 70))
    assert r.screen[0] == 10
