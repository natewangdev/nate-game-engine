from __future__ import annotations

from nge2.geom import generate_path


def test_path_has_waypoints():
    path = generate_path((0, 0), (100, 0), duration=0.05, rng=__import__("random").Random(0))
    assert len(path) >= 2
    assert path[-1].x != 0 or path[-1].y == 0


def test_zero_distance():
    path = generate_path((5, 5), (5, 5))
    assert len(path) == 1
