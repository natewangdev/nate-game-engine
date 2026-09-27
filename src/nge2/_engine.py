"""NGE2 engine facade."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import TracebackType
from typing import Any

from nge2._errors import ClosedError, ConstructError
from nge2.capture import Capture, create_capture
from nge2.control import Control
from nge2.control import _port_registry as port_registry
from nge2.control._transport import SerialTransport, TransportError, find_port
from nge2.find import Find
from nge2.log import (
    attach_engine_logging,
    detach_handlers,
    get_logger,
    resolve_log_dir,
    save_error_screenshot,
)
from nge2.ocr import Ocr
from nge2.window import Window, primary_screen_size, set_process_dpi_aware
from nge2.yolo import Yolo

log = get_logger(__name__)

CaptureFactory = Callable[[str], Capture]
TransportFactory = Callable[[], Any]
VisionFactory = Callable[..., Any]


def _resolve_model(resource_dir: Path, path: str | Path, *, label: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = resource_dir / p
    p = p.resolve()
    if not p.is_file():
        raise ConstructError(f"{label} not found: {p}")
    return p


def _resolve_optional(resource_dir: Path, path: str | Path | None) -> Path | None:
    if path is None:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = resource_dir / p
    p = p.resolve()
    return p  # may be missing; callers decide


class NGE2:
    """Nate Game Engine instance."""

    def __init__(
        self,
        resource_dir: str | Path,
        *,
        capture: str = "dxcam",
        hwnd: int | None = None,
        humanize: bool = True,
        control_mode: int = 2,
        capture_factory: CaptureFactory | None = None,
        transport_factory: TransportFactory | None = None,
        log_dir: str | Path | None = None,
        yolo_model: str | Path = "models/yolo.onnx",
        yolo_names: str | Path | None = "models/yolo.names",
        ocr_kwargs: dict[str, Any] | None = None,
        ocr_factory: VisionFactory | None = None,
        yolo_factory: VisionFactory | None = None,
    ) -> None:
        if resource_dir is None or str(resource_dir).strip() == "":
            raise ConstructError("resource_dir is required")
        self.resource_dir = Path(resource_dir)
        if not self.resource_dir.is_absolute():
            self.resource_dir = (Path.cwd() / self.resource_dir).resolve()
        else:
            self.resource_dir = self.resource_dir.resolve()

        if capture not in ("dxcam", "mss"):
            raise ConstructError(f"Invalid capture backend: {capture!r}")
        self._capture_name = capture
        self._humanize = bool(humanize)
        self._control_mode = int(control_mode)
        self._hwnd = hwnd
        self._closed = False
        self._held_port: str | None = None
        self._capture_factory = capture_factory or create_capture
        self._transport_factory = transport_factory
        self.log_dir = resolve_log_dir(log_dir)
        self._log_path: Path | None = None
        self._log_handlers: list = []

        if self._control_mode in (0, 1):
            raise ConstructError(
                f"control_mode={self._control_mode} is not implemented "
                "(API reserved for foreground/background backends)"
            )
        if self._control_mode != 2:
            raise ConstructError(f"Unsupported control_mode={self._control_mode}")

        set_process_dpi_aware()

        try:
            self._capture = self._capture_factory(self._capture_name)
        except Exception as exc:
            raise ConstructError(str(exc)) from exc

        self.window = Window(hwnd)
        self.find = Find(
            resource_dir=self.resource_dir,
            capture=self._capture,
            window=self.window,
        )
        self.log = get_logger("engine")

        # OCR / YOLO — load before HID so failure does not hold the serial port.
        try:
            if ocr_factory is not None:
                self.ocr = ocr_factory(
                    capture=self._capture,
                    window=self.window,
                    resource_dir=self.resource_dir,
                    engine_kwargs=ocr_kwargs,
                )
            else:
                self.ocr = Ocr(
                    capture=self._capture,
                    window=self.window,
                    engine_kwargs=ocr_kwargs,
                )
            if yolo_factory is not None:
                self.yolo = yolo_factory(
                    capture=self._capture,
                    window=self.window,
                    resource_dir=self.resource_dir,
                    model_path=yolo_model,
                    names_path=yolo_names,
                )
            else:
                ypath = _resolve_model(self.resource_dir, yolo_model, label="YOLO model")
                npath = _resolve_optional(self.resource_dir, yolo_names)
                self.yolo = Yolo(
                    capture=self._capture,
                    window=self.window,
                    model_path=ypath,
                    names_path=npath if npath is not None and npath.is_file() else None,
                )
        except ConstructError:
            self._capture.release()
            raise
        except Exception as exc:
            self._capture.release()
            raise ConstructError(str(exc)) from exc

        try:
            if self._transport_factory is not None:
                transport = self._transport_factory()
                if hasattr(transport, "open"):
                    transport = transport.open()
            else:
                transport = SerialTransport().open()
            port = getattr(transport, "port", None)
            if port and not port_registry.try_acquire(str(port)):
                try:
                    transport.close()
                except Exception:  # noqa: BLE001
                    pass
                raise ConstructError(
                    f"HID serial port {port!r} is busy (held by another NGE2 instance)"
                )
            self._held_port = str(port) if port else None
            if not transport.ping():
                if self._held_port:
                    port_registry.release(self._held_port)
                try:
                    transport.close()
                except Exception:  # noqa: BLE001
                    pass
                raise ConstructError("ESP32-S3 device did not respond to PING")
        except ConstructError:
            self._capture.release()
            raise
        except TransportError as exc:
            self._capture.release()
            if find_port() is None and self._transport_factory is None:
                raise ConstructError(
                    "No ESP32-S3 serial port found (control_mode=2)"
                ) from exc
            raise ConstructError(str(exc)) from exc
        except Exception as exc:
            self._capture.release()
            if self._held_port:
                port_registry.release(self._held_port)
            raise ConstructError(str(exc)) from exc

        self._control = Control(
            transport,
            humanize=self._humanize,
            screen_size=primary_screen_size(),
            window=self.window,
        )

        self._log_path, self._log_handlers = attach_engine_logging(
            self.log_dir,
            self._on_error_screenshot,
        )
        log.info(
            "NGE2 ready capture=%s hwnd=%s humanize=%s port=%s log=%s",
            self._capture_name,
            hwnd,
            self._humanize,
            self._held_port,
            self._log_path,
        )

    def _on_error_screenshot(self, message: str) -> None:
        warn = get_logger("log")
        try:
            if self._closed:
                raise RuntimeError("engine is closed")
            frame = self._capture.grab(region=None)
            client = self.window.client_region
            if client is not None:
                l, t, r, b = client.screen
                h, w = frame.shape[:2]
                l = max(0, min(int(l), w))
                r = max(0, min(int(r), w))
                t = max(0, min(int(t), h))
                b = max(0, min(int(b), h))
                if r > l and b > t:
                    frame = frame[t:b, l:r].copy()
            if self._log_path is None:
                raise RuntimeError("log path not set")
            shot_dir = self._log_path.parent / "screenshot"
            path = save_error_screenshot(frame, message, shot_dir)
            warn.warning("ERROR screenshot saved: %s", path)
        except Exception as exc:  # noqa: BLE001
            warn.warning("ERROR screenshot failed: %s", exc)

    @property
    def capture(self) -> Capture:
        self._ensure_open()
        return self._capture

    @property
    def control(self) -> Control:
        self._ensure_open()
        return self._control

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            close_ocr = getattr(self.ocr, "close", None)
            if callable(close_ocr):
                close_ocr()
        except Exception:  # noqa: BLE001
            pass
        try:
            close_yolo = getattr(self.yolo, "close", None)
            if callable(close_yolo):
                close_yolo()
        except Exception:  # noqa: BLE001
            pass
        try:
            self._control.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            self._capture.release()
        except Exception:  # noqa: BLE001
            pass
        port_registry.release(self._held_port)
        self._held_port = None
        log.info("NGE2 closed")
        detach_handlers(self._log_handlers)
        self._log_handlers = []

    def _ensure_open(self) -> None:
        if self._closed:
            raise ClosedError("NGE2 is closed; create a new instance")

    def __enter__(self) -> NGE2:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
