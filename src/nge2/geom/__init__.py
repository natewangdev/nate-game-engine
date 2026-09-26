"""Human-like mouse path generation (internal; not a stable public API)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class Waypoint:
    x: float
    y: float
    delay: float


@dataclass
class HumanizeConfig:
    curvature: float = 0.1
    jitter: float = 0.4
    overshoot_chance: float = 0
    overshoot_pixels: float = 14.0
    rate_hz: float = 144.0
    timing_noise: float = 0.1
    max_speed: float = 0
    pause_chance: float = 0.00
    pause_range: tuple[float, float] = (0.04, 0.14)


def _ease_in_out(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _cubic_bezier(p0, p1, p2, p3, t: float) -> tuple[float, float]:
    u = 1.0 - t
    a = u * u * u
    b = 3 * u * u * t
    c = 3 * u * t * t
    d = t * t * t
    x = a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0]
    y = a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]
    return x, y


def _control_point(p0, p3, frac: float, spread: float, rng: random.Random):
    bx = p0[0] + (p3[0] - p0[0]) * frac
    by = p0[1] + (p3[1] - p0[1]) * frac
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    offset = rng.uniform(-spread, spread)
    return bx + nx * offset, by + ny * offset


def _limit_speed(
    waypoints: list[Waypoint],
    origin: tuple[float, float],
    max_speed: float,
) -> None:
    if max_speed <= 0:
        return
    prev = origin
    for wp in waypoints:
        seg = math.hypot(wp.x - prev[0], wp.y - prev[1])
        min_delay = seg / max_speed
        wp.delay = max(wp.delay, min_delay)
        prev = (wp.x, wp.y)


def _apply_pauses(
    waypoints: list[Waypoint],
    cfg: HumanizeConfig,
    rng: random.Random,
) -> None:
    if cfg.pause_chance <= 0:
        return
    for wp in waypoints[:-1]:
        if rng.random() < cfg.pause_chance:
            wp.delay += rng.uniform(*cfg.pause_range)


def generate_path(
    start: tuple[float, float],
    end: tuple[float, float],
    duration: float | None = None,
    config: HumanizeConfig | None = None,
    rng: random.Random | None = None,
) -> list[Waypoint]:
    """Generate timed waypoints from ``start`` to ``end``."""
    cfg = config or HumanizeConfig()
    rng = rng or random.Random()

    dist = math.hypot(end[0] - start[0], end[1] - start[1])
    if dist < 1e-3:
        return [Waypoint(end[0], end[1], 0.0)]

    if duration is None:
        duration = 0.05 + dist / 2600.0
        duration *= rng.uniform(0.85, 1.20)

    spread = cfg.curvature * dist
    c1 = _control_point(start, end, rng.uniform(0.25, 0.45), spread, rng)
    c2 = _control_point(start, end, rng.uniform(0.55, 0.75), spread, rng)

    target = end
    overshoot = None
    if rng.random() < cfg.overshoot_chance:
        ang = math.atan2(end[1] - start[1], end[0] - start[0])
        over = rng.uniform(0.4, 1.0) * cfg.overshoot_pixels
        overshoot = (end[0] + math.cos(ang) * over, end[1] + math.sin(ang) * over)
        target = overshoot

    steps = max(2, int(duration * cfg.rate_hz))
    base_delay = duration / steps

    waypoints: list[Waypoint] = []
    for i in range(1, steps + 1):
        t = _ease_in_out(i / steps)
        x, y = _cubic_bezier(start, c1, c2, target, t)
        if cfg.jitter and i != steps:
            x += rng.uniform(-cfg.jitter, cfg.jitter)
            y += rng.uniform(-cfg.jitter, cfg.jitter)
        noise = 1.0 + rng.uniform(-cfg.timing_noise, cfg.timing_noise)
        waypoints.append(Waypoint(x, y, base_delay * noise))

    if overshoot is not None:
        correct_steps = rng.randint(3, 6)
        for i in range(1, correct_steps + 1):
            t = _ease_in_out(i / correct_steps)
            x = overshoot[0] + (end[0] - overshoot[0]) * t
            y = overshoot[1] + (end[1] - overshoot[1]) * t
            waypoints.append(Waypoint(x, y, base_delay * rng.uniform(0.8, 1.3)))

    _limit_speed(waypoints, start, cfg.max_speed)
    _apply_pauses(waypoints, cfg, rng)
    return waypoints
