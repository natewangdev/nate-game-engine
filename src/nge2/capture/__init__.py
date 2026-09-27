"""Screen capture — BGR frames via dxcam or mss (first display)."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from nge2._errors import CaptureError
from nge2.log import get_logger

log = get_logger(__name__)

_comtypes_finalizer_patched = False
CaptureFactory = Callable[[str], "Capture"]


def _silence_comtypes_finalizer() -> None:
    global _comtypes_finalizer_patched
    if _comtypes_finalizer_patched:
        return
    try:
        from comtypes._post_coinit import unknwn as _unknwn

        base = _unknwn._compointer_base
    except Exception:  # noqa: BLE001
        try:
            import comtypes

            base = comtypes._compointer_base  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            return

    original_del = getattr(base, "__del__", None)
    if original_del is None:
        return

    def _safe_del(self) -> None:
        try:
            original_del(self)
        except Exception:  # noqa: BLE001
            pass

    base.__del__ = _safe_del
    _comtypes_finalizer_patched = True


class Capture:
    """BGR screen capture for one ``NGE2`` instance."""

    def __init__(self, backend: str = "dxcam") -> None:
        if backend not in ("dxcam", "mss"):
            raise CaptureError(f"Unknown capture backend: {backend!r}")
        self.backend_name = backend
        self._dxcam: object | None = None
        self._mss: object | None = None
        self._active = False
        self._open_backend()

    def _open_backend(self) -> None:
        name = self.backend_name
        if name == "dxcam":
            try:
                import dxcam

                _silence_comtypes_finalizer()
                # Prefer numpy processor so OpenCV (cv2) is not required.
                self._dxcam = dxcam.create(
                    output_color="BGR",
                    processor_backend="numpy",
                )
                self._active = True
                log.info("Capture backend: dxcam")
                return
            except Exception as exc:
                raise CaptureError(
                    f"Capture backend 'dxcam' is unavailable: {exc}"
                ) from exc
        try:
            import mss

            self._mss = mss.mss()
            self._active = True
            log.info("Capture backend: mss")
        except Exception as exc:
            raise CaptureError(f"Capture backend 'mss' is unavailable: {exc}") from exc

    def grab(
        self,
        region: tuple[int, int, int, int] | None = None,
    ) -> np.ndarray:
        """Return a BGR frame; ``region`` is screen physical pixels ``(l,t,r,b)``."""
        if not self._active:
            self._open_backend()

        if self.backend_name == "dxcam":
            frame = self._dxcam.grab(region=region)  # type: ignore[union-attr]
            if frame is None:
                frame = self._dxcam.grab(region=region)  # type: ignore[union-attr]
            if frame is None:
                raise CaptureError("dxcam returned no frame")
            return np.asarray(frame)

        if region:
            l, t, r, b = region
            mon = {
                "left": int(l),
                "top": int(t),
                "width": max(0, int(r - l)),
                "height": max(0, int(b - t)),
            }
        else:
            mon = self._mss.monitors[1]  # type: ignore[union-attr]
        raw = self._mss.grab(mon)  # type: ignore[union-attr]
        arr = np.asarray(raw)
        return arr[:, :, :3].copy()

    def release(self) -> None:
        if self._dxcam is not None:
            try:
                self._dxcam.release()  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                pass
            self._dxcam = None
        if self._mss is not None:
            try:
                self._mss.close()  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                pass
            self._mss = None
        self._active = False
        log.info("Capture backend released (%s)", self.backend_name)


def create_capture(backend: str) -> Capture:
    return Capture(backend=backend)
