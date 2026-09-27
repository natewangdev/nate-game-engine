from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import pytest

from fakes import FakeCapture, FakeTransport
from nge2._engine import NGE2
from nge2._errors import FindError
from nge2.find import Find, Match
from nge2.window import ClientRegion, Window


@dataclass
class FakeBoundWindow:
    """Duck-typed Window with fixed client→screen offset."""

    hwnd: int = 1
    _screen: tuple[int, int, int, int] = (100, 50, 400, 250)

    @property
    def client_region(self) -> ClientRegion:
        l, t, r, b = self._screen
        return ClientRegion(local=(0, 0, r - l, b - t), screen=self._screen)

    def client_to_screen(self, x: float, y: float) -> tuple[float, float]:
        sx, sy, _, _ = self._screen
        return sx + x, sy + y

    def screen_to_client(self, x: float, y: float) -> tuple[float, float]:
        sx, sy, _, _ = self._screen
        return x - sx, y - sy


def _engine(tmp_path, frame: np.ndarray, hwnd=None):
    cap = FakeCapture(frame=frame)
    return NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: cap,
        transport_factory=lambda: FakeTransport(),
        hwnd=hwnd,
        log_dir=tmp_path / "logs",
    ), cap


def _save_template(path, arr: np.ndarray) -> None:
    ok, buf = cv2.imencode(".png", arr)
    assert ok
    path.write_bytes(buf.tobytes())


def test_find_image_center_and_fresh_grab(tmp_path):
    frame = np.zeros((200, 300, 3), dtype=np.uint8)
    tmpl = np.random.randint(40, 220, (20, 30, 3), dtype=np.uint8)
    frame[40:60, 100:130] = tmpl
    _save_template(tmp_path / "btn.png", tmpl)

    engine, cap = _engine(tmp_path, frame)
    try:
        m = engine.find.find_image("btn.png")
        assert isinstance(m, Match)
        assert m.x == 115
        assert m.y == 50
        assert m.width == 30 and m.height == 20
        assert m.score >= 0.99
        assert cap.grabs == 1
        engine.find.find_image("btn.png")
        assert cap.grabs == 2
    finally:
        engine.close()


def test_find_image_miss_and_missing_file(tmp_path):
    frame = np.zeros((80, 80, 3), dtype=np.uint8)
    # Patterned template that cannot match a blank frame under high threshold.
    other = np.zeros((12, 12, 3), dtype=np.uint8)
    other[0:6, 0:6] = (0, 0, 255)
    other[6:12, 6:12] = (0, 255, 0)
    _save_template(tmp_path / "other.png", other)
    engine, _ = _engine(tmp_path, frame)
    try:
        assert engine.find.find_image("other.png", threshold=0.8) is None
        with pytest.raises(FileNotFoundError):
            engine.find.find_image("nope.png")
    finally:
        engine.close()


def test_find_images_nms(tmp_path):
    frame = np.zeros((120, 200, 3), dtype=np.uint8)
    tmpl = np.random.randint(30, 200, (15, 15, 3), dtype=np.uint8)
    frame[10:25, 20:35] = tmpl
    frame[10:25, 100:115] = tmpl
    _save_template(tmp_path / "icon.png", tmpl)

    engine, _ = _engine(tmp_path, frame)
    try:
        hits = engine.find.find_images("icon.png", threshold=0.9)
        assert len(hits) == 2
        centers = sorted((h.x, h.y) for h in hits)
        # Centers: left+tw/2, top+th/2 → round(20+7.5)=28, round(10+7.5)=18
        assert centers == [(28, 18), (108, 18)]
        blank = np.zeros((15, 15, 3), dtype=np.uint8)
        blank[0, 0] = (1, 2, 3)
        _save_template(tmp_path / "blankish.png", blank)
        assert engine.find.find_images("blankish.png", threshold=0.95) == []
    finally:
        engine.close()


def test_find_color_single_and_multi(tmp_path):
    frame = np.zeros((50, 50, 3), dtype=np.uint8)
    # BGR: red pixel at (10, 20)
    frame[20, 10] = (0, 0, 255)
    frame[30, 15] = (0, 0, 250)

    engine, _ = _engine(tmp_path, frame)
    try:
        one = engine.find.find_color((255, 0, 0), tolerance=10)
        assert one is not None
        assert (one.x, one.y) == (10, 20)
        assert one.color == (255, 0, 0)
        assert engine.find.find_color("#00FF00") is None
        many = engine.find.find_color("#FF0000", tolerance=10, multi=True)
        assert isinstance(many, list)
        assert len(many) == 2
        assert engine.find.find_color((0, 255, 0), multi=True) == []
    finally:
        engine.close()


def test_find_region_and_hwnd_coords(tmp_path):
    # Full "screen" frame; client at (100,50)-(400,250)
    frame = np.zeros((300, 500, 3), dtype=np.uint8)
    tmpl = np.random.randint(50, 200, (12, 12, 3), dtype=np.uint8)
    # Place template at screen (150, 80) → client (50, 30); center client (56, 36)
    frame[80:92, 150:162] = tmpl
    _save_template(tmp_path / "t.png", tmpl)

    cap = FakeCapture(frame=frame)
    finder = Find(resource_dir=tmp_path, capture=cap, window=FakeBoundWindow())  # type: ignore[arg-type]
    m = finder.find_image("t.png")
    assert m is not None
    assert (m.x, m.y) == (56, 36)

    # Region client (40,20)-(80,60) still contains the template
    m2 = finder.find_image("t.png", region=(40, 20, 80, 60))
    assert m2 is not None
    assert (m2.x, m2.y) == (56, 36)


def test_invalid_region_and_color(tmp_path):
    cap = FakeCapture(frame=np.zeros((40, 40, 3), dtype=np.uint8))
    finder = Find(resource_dir=tmp_path, capture=cap, window=Window(None))
    with pytest.raises(FindError):
        finder.find_color((1, 2, 3), region=(10, 10, 5, 20))
    with pytest.raises(ValueError):
        finder.find_color("not-a-color")


def test_template_larger_than_region(tmp_path):
    frame = np.zeros((30, 30, 3), dtype=np.uint8)
    big = np.ones((40, 40, 3), dtype=np.uint8) * 90
    _save_template(tmp_path / "big.png", big)
    engine, _ = _engine(tmp_path, frame)
    try:
        assert engine.find.find_image("big.png") is None
        assert engine.find.find_images("big.png") == []
    finally:
        engine.close()


def test_screen_to_client_passthrough():
    w = Window(None)
    assert w.screen_to_client(10, 20) == (10, 20)
