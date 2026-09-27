"""Window binding helpers (Win32 client area, DPI-aware)."""

from __future__ import annotations

from dataclasses import dataclass

from nge2._errors import WindowError
from nge2.log import get_logger

log = get_logger(__name__)


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


class Window:
    """Bound window queries for one engine."""

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
