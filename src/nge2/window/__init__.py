"""Window binding helpers (Win32 client area, DPI-aware) and window ops."""

from __future__ import annotations

from dataclasses import dataclass

from nge2._errors import WindowError
from nge2.log import get_logger

log = get_logger(__name__)

# ShowWindow
_SW_RESTORE = 9
# SetWindowPos
_HWND_TOPMOST = -1
_HWND_NOTOPMOST = -2
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_NOZORDER = 0x0004
_SWP_NOACTIVATE = 0x0010
_SWP_SHOWWINDOW = 0x0040


def set_process_dpi_aware() -> None:
    """Declare the process DPI-aware (physical pixels)."""
    try:
        import ctypes

        user32 = ctypes.windll.user32
        # Prefer Per-Monitor V2 when available.
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except Exception:  # noqa: BLE001
            user32.SetProcessDPIAware()
    except Exception as exc:  # noqa: BLE001
        log.debug("DPI awareness not set: %s", exc)


def primary_screen_size() -> tuple[int, int]:
    try:
        import ctypes

        user32 = ctypes.windll.user32
        return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))
    except Exception:  # noqa: BLE001
        return 1920, 1080


@dataclass(frozen=True)
class ClientRegion:
    """Client visual region."""

    local: tuple[int, int, int, int]  # (l, t, r, b) in client coords
    screen: tuple[int, int, int, int]  # screen physical pixels


@dataclass(frozen=True)
class WindowMatch:
    """One visible top-level window from find_by_title."""

    hwnd: int
    title: str
    rect: tuple[int, int, int, int]  # outer frame screen LTRB


def _list_visible_toplevel() -> list[WindowMatch]:
    """Enumerate visible top-level windows (monkeypatch seam for tests)."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    matches: list[WindowMatch] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def _enum(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        if not title:
            return True
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return True
        matches.append(
            WindowMatch(
                hwnd=int(hwnd),
                title=title,
                rect=(int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)),
            )
        )
        return True

    if not user32.EnumWindows(_enum, 0):
        raise WindowError("EnumWindows failed")
    return matches


def _activate_hwnd(hwnd: int) -> None:
    """Bring hwnd to the foreground (monkeypatch seam)."""
    import ctypes

    user32 = ctypes.windll.user32
    if not user32.IsWindow(hwnd):
        raise WindowError(f"Invalid or destroyed hwnd={hwnd}")
    user32.ShowWindow(hwnd, _SW_RESTORE)
    if not user32.SetForegroundWindow(hwnd):
        raise WindowError(f"SetForegroundWindow failed for hwnd={hwnd}")


def _set_topmost_hwnd(hwnd: int, enabled: bool) -> None:
    """Set or clear always-on-top (monkeypatch seam)."""
    import ctypes

    user32 = ctypes.windll.user32
    if not user32.IsWindow(hwnd):
        raise WindowError(f"Invalid or destroyed hwnd={hwnd}")
    insert_after = _HWND_TOPMOST if enabled else _HWND_NOTOPMOST
    flags = _SWP_NOMOVE | _SWP_NOSIZE | _SWP_NOACTIVATE
    ok = user32.SetWindowPos(hwnd, insert_after, 0, 0, 0, 0, flags)
    if not ok:
        raise WindowError(f"SetWindowPos(topmost={enabled}) failed for hwnd={hwnd}")


def _move_hwnd(hwnd: int, x: int, y: int) -> None:
    """Move outer-frame top-left to screen (x, y); keep size (monkeypatch seam)."""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    if not user32.IsWindow(hwnd):
        raise WindowError(f"Invalid or destroyed hwnd={hwnd}")
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise WindowError(f"GetWindowRect failed for hwnd={hwnd}")
    width = int(rect.right) - int(rect.left)
    height = int(rect.bottom) - int(rect.top)
    flags = _SWP_NOZORDER | _SWP_NOACTIVATE | _SWP_SHOWWINDOW
    ok = user32.SetWindowPos(hwnd, 0, int(x), int(y), width, height, flags)
    if not ok:
        raise WindowError(f"SetWindowPos(move) failed for hwnd={hwnd}")


class Window:
    """Bound window queries and management for one engine."""

    def __init__(self, hwnd: int | None) -> None:
        self._hwnd = hwnd

    @property
    def hwnd(self) -> int | None:
        return self._hwnd

    @property
    def title(self) -> str:
        if self._hwnd is None:
            return ""
        try:
            import ctypes

            user32 = ctypes.windll.user32
            length = user32.GetWindowTextLengthW(self._hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(self._hwnd, buf, length + 1)
            return buf.value
        except Exception as exc:
            raise WindowError(f"Failed to read window title: {exc}") from exc

    @property
    def client_region(self) -> ClientRegion | None:
        if self._hwnd is None:
            return None
        return self._client_region(self._hwnd)

    @staticmethod
    def _client_region(hwnd: int) -> ClientRegion:
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            rect = wintypes.RECT()
            if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
                raise WindowError(f"GetClientRect failed for hwnd={hwnd}")
            local = (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
            pt = wintypes.POINT(0, 0)
            if not user32.ClientToScreen(hwnd, ctypes.byref(pt)):
                raise WindowError(f"ClientToScreen failed for hwnd={hwnd}")
            w = local[2] - local[0]
            h = local[3] - local[1]
            screen = (int(pt.x), int(pt.y), int(pt.x + w), int(pt.y + h))
            return ClientRegion(local=local, screen=screen)
        except WindowError:
            raise
        except Exception as exc:
            raise WindowError(f"Invalid or destroyed hwnd={hwnd}: {exc}") from exc

    def client_to_screen(self, x: float, y: float) -> tuple[float, float]:
        """Map client-relative physical pixels to screen coordinates."""
        if self._hwnd is None:
            return x, y
        region = self._client_region(self._hwnd)
        sx, sy, _, _ = region.screen
        return sx + x, sy + y

    def screen_to_client(self, x: float, y: float) -> tuple[float, float]:
        """Map screen physical pixels to client-relative coordinates."""
        if self._hwnd is None:
            return x, y
        region = self._client_region(self._hwnd)
        sx, sy, _, _ = region.screen
        return x - sx, y - sy

    def _resolve_hwnd(self, hwnd: int | None) -> int:
        target = self._hwnd if hwnd is None else hwnd
        if target is None:
            raise WindowError("No window hwnd: bind at construct or pass hwnd=")
        return int(target)

    def find_by_title(self, query: str) -> list[WindowMatch]:
        """Find visible top-level windows whose titles contain ``query`` (case-insensitive)."""
        if not isinstance(query, str) or not query.strip():
            raise WindowError("find_by_title query must be a non-blank string")
        needle = query.casefold()
        return [m for m in _list_visible_toplevel() if needle in m.title.casefold()]

    def activate(self, hwnd: int | None = None) -> None:
        """Bring the target window to the foreground."""
        _activate_hwnd(self._resolve_hwnd(hwnd))

    def set_topmost(self, enabled: bool, hwnd: int | None = None) -> None:
        """Enable or disable always-on-top for the target window."""
        _set_topmost_hwnd(self._resolve_hwnd(hwnd), bool(enabled))

    def move(self, x: int, y: int, hwnd: int | None = None) -> None:
        """Move outer-frame top-left to screen physical pixels ``(x, y)``; keep size."""
        _move_hwnd(self._resolve_hwnd(hwnd), int(x), int(y))
