"""HID control facade (ESP32-S3)."""

from __future__ import annotations

import math
import random
import time
from typing import Protocol

from nge2._errors import ClosedError, ControlError
from nge2.control._keymap import resolve_key, resolve_modifiers
from nge2.geom import HumanizeConfig, generate_path
from nge2.log import get_logger
from nge2.window import Window

log = get_logger(__name__)

HID_MAX = 32767
DEFAULT_SPREAD = 10.0


class Transport(Protocol):
    port: str | None

    def command(self, line: str, expect: str = "OK") -> str: ...

    def close(self) -> None: ...

    def ping(self) -> bool: ...


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else (min(v, hi))


def _require_xy_pair(x: float | None, y: float | None, *, what: str) -> None:
    if (x is None) ^ (y is None):
        raise ControlError(f"{what} requires both x and y, or neither")


def _require_positive_int(value: object, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ControlError(f"{name} must be a positive integer")
    return value


class Control:
    """Mouse/keyboard control over a HID transport."""

    def __init__(
        self,
        transport: Transport,
        *,
        humanize: bool = True,
        screen_size: tuple[int, int] | None = None,
        window: Window | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self._transport = transport
        self._humanize = humanize
        self._humanize_cfg = HumanizeConfig()
        self._window = window or Window(None)
        self.rng = rng or random.Random()
        if screen_size is None:
            from nge2.window import primary_screen_size

            screen_size = primary_screen_size()
        self.screen_size = screen_size
        w, h = screen_size
        self._pos = (w / 2.0, h / 2.0)
        self._closed = False
        log.info("Control screen size = %dx%d humanize=%s", w, h, humanize)

    def _ensure_open(self) -> None:
        if self._closed:
            raise ClosedError("Control is closed")

    def _to_device(self, px: float, py: float) -> tuple[int, int]:
        w, h = self.screen_size
        x = int(round(_clamp(px, 0, w - 1) * HID_MAX / max(1, w - 1)))
        y = int(round(_clamp(py, 0, h - 1) * HID_MAX / max(1, h - 1)))
        return x, y

    def _emit(self, px: float, py: float) -> None:
        dx, dy = self._to_device(px, py)
        self._transport.command(f"MA {dx} {dy}")
        self._pos = (px, py)

    def _scatter(self, px: float, py: float, spread: float) -> tuple[float, float]:
        if spread <= 0:
            return px, py
        angle = self.rng.uniform(0.0, 2.0 * math.pi)
        radius = spread * math.sqrt(self.rng.random())
        return px + math.cos(angle) * radius, py + math.sin(angle) * radius

    def _to_screen(self, x: float, y: float) -> tuple[float, float]:
        try:
            return self._window.client_to_screen(x, y)
        except Exception as exc:
            raise ControlError(str(exc)) from exc

    def move(
        self,
        x: float,
        y: float,
        duration: float | None = None,
        spread: float = DEFAULT_SPREAD,
    ) -> None:
        self._ensure_open()
        sx, sy = self._to_screen(x, y)
        if not self._humanize:
            self._emit(sx, sy)
            return
        tx, ty = self._scatter(sx, sy, spread)
        path = generate_path(
            self._pos,
            (tx, ty),
            duration=duration,
            config=self._humanize_cfg,
            rng=self.rng,
        )
        for wp in path:
            if wp.delay > 0:
                time.sleep(wp.delay)
            self._emit(wp.x, wp.y)

    def left_click(self, hold: float | None = None) -> None:
        self.move_and_click(button="L", hold=hold)

    def right_click(self, hold: float | None = None) -> None:
        self.move_and_click(button="R", hold=hold)

    def left_down(self) -> None:
        self._button("L", down=True)

    def left_up(self) -> None:
        self._button("L", down=False)

    def right_down(self) -> None:
        self._button("R", down=True)

    def right_up(self) -> None:
        self._button("R", down=False)

    def _button(self, button: str, *, down: bool) -> None:
        self._ensure_open()
        state = 1 if down else 0
        self._transport.command(f"BTN {button.upper()} {state}")

    def drag(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        button: str = "L",
        duration: float | None = None,
        spread: float = DEFAULT_SPREAD,
    ) -> None:
        """Move to start, press button, move to end, release (default left)."""
        self._ensure_open()
        btn = button.upper()
        if btn not in ("L", "R"):
            raise ControlError(f"drag button must be 'L' or 'R', got {button!r}")
        self.move(x1, y1, duration=duration, spread=spread)
        self._button(btn, down=True)
        time.sleep(self.rng.uniform(0.02, 0.06))
        try:
            self.move(x2, y2, duration=duration, spread=spread)
        finally:
            self._button(btn, down=False)

    def scroll(self, direction: str, notches: int = 1) -> None:
        """Scroll wheel at current position. ``direction`` is ``up`` or ``down``."""
        self._ensure_open()
        n = _require_positive_int(notches, name="notches")
        d = direction.lower().strip()
        if d not in ("up", "down"):
            raise ControlError(f"scroll direction must be 'up' or 'down', got {direction!r}")
        delta = n if d == "up" else -n
        delta = int(_clamp(delta, -127, 127))
        self._transport.command(f"WHEEL {delta}")

    def double_click(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        hold: float | None = None,
        interval: float | None = None,
        duration: float | None = None,
    ) -> None:
        """Left-button double-click at optional target or current position.

        Both clicks occur at the same point (pre-move uses ``spread=0``; no scatter).
        """
        self._ensure_open()
        _require_xy_pair(x, y, what="double_click")
        if x is not None and y is not None:
            self.move(x, y, duration=duration, spread=0.0)
            time.sleep(self.rng.uniform(0.02, 0.06))
        self.move_and_click(button="L", hold=hold)
        gap = interval if interval is not None else self.rng.uniform(0.04, 0.08)
        if gap > 0:
            time.sleep(gap)
        self.move_and_click(button="L", hold=hold)

    def move_and_click(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        button: str = "L",
        hold: float | None = None,
        duration: float | None = None,
        spread: float = DEFAULT_SPREAD,
    ) -> None:
        self._ensure_open()
        if x is not None and y is not None:
            self.move(x, y, duration=duration, spread=spread)
            time.sleep(self.rng.uniform(0.02, 0.06))
        hold_ms = int(hold * 1000) if hold is not None else self.rng.randint(45, 110)
        self._transport.command(f"CLK {button.upper()} {hold_ms}")

    def key_down(self, key: str) -> None:
        self._ensure_open()
        try:
            usage = resolve_key(key)
        except KeyError as exc:
            raise ControlError(str(exc)) from exc
        self._transport.command(f"KD {usage}")

    def key_up(self, key: str) -> None:
        self._ensure_open()
        try:
            usage = resolve_key(key)
        except KeyError as exc:
            raise ControlError(str(exc)) from exc
        self._transport.command(f"KU {usage}")

    def key_click(self, *keys: str, hold: float | None = None) -> None:
        """Click a key or chord: ``key_click('a')`` or ``key_click('ctrl', 'c')``."""
        self._ensure_open()
        if not keys:
            raise ControlError("key_click requires at least one key")
        *mods, main = keys
        try:
            if mods:
                self._transport.command(f"MOD {resolve_modifiers(*mods)}")
            hold_ms = int(hold * 1000) if hold is not None else self.rng.randint(40, 90)
            self._transport.command(f"KP {resolve_key(main)} {hold_ms}")
            time.sleep(self.rng.uniform(0.02, 0.05))
        except KeyError as exc:
            raise ControlError(str(exc)) from exc
        finally:
            if mods:
                try:
                    self._transport.command("MOD 0")
                except Exception:  # noqa: BLE001
                    pass

    def hotkey(self, *keys: str, hold: float | None = None) -> None:
        """Alias of :meth:`key_click` for modifier chords (``*keys`` form only)."""
        self.key_click(*keys, hold=hold)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._transport.command("STOP")
        except Exception:  # noqa: BLE001
            pass
        try:
            self._transport.close()
        except Exception:  # noqa: BLE001
            pass
