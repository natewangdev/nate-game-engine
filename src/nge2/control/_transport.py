"""USB CDC serial transport to ESP32-S3 HID firmware."""

from __future__ import annotations

import time
from dataclasses import dataclass

import serial
from serial.tools import list_ports

from nge2.log import get_logger

log = get_logger(__name__)

ESP32S3_HINTS = ("303a",)


class TransportError(RuntimeError):
    """Raised when the device does not acknowledge a command."""


def find_port(vid_hints: tuple[str, ...] = ESP32S3_HINTS) -> str | None:
    """Return the first serial port that looks like an ESP32-S3, or ``None``."""
    for port in list_ports.comports():
        hwid = (port.hwid or "").lower()
        if any(hint in hwid for hint in vid_hints):
            return port.device
    return None


@dataclass
class SerialTransport:
    """Synchronous, line-oriented serial transport."""

    port: str | None = None
    baudrate: int = 115200
    timeout: float = 0.5
    _serial: serial.Serial | None = None

    def open(self) -> SerialTransport:
        port = self.port or find_port()
        if port is None:
            raise TransportError(
                "No ESP32-S3 serial port found. Pass port=... explicitly."
            )
        self.port = port
        self._serial = serial.Serial(port, self.baudrate, timeout=self.timeout)
        time.sleep(0.2)
        self._serial.reset_input_buffer()
        log.info("Opened serial transport on %s", port)
        return self

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            try:
                self.command("STOP")
            except TransportError:
                pass
            self._serial.close()
            log.info("Closed serial transport")
        self._serial = None

    def __enter__(self) -> SerialTransport:
        return self.open()

    def __exit__(self, *exc: object) -> None:
        self.close()

    def command(self, line: str, expect: str = "OK") -> str:
        if self._serial is None:
            raise TransportError("Transport is not open")

        payload = (line.strip() + "\n").encode("ascii")
        self._serial.write(payload)
        self._serial.flush()

        reply = self._serial.readline().decode("ascii", errors="replace").strip()
        if not reply:
            raise TransportError(f"Timed out waiting for reply to {line!r}")
        if reply == "ERR":
            raise TransportError(f"Device rejected command {line!r}")
        if expect and reply != expect:
            raise TransportError(
                f"Unexpected reply to {line!r}: got {reply!r}, want {expect!r}"
            )
        return reply

    def ping(self) -> bool:
        try:
            return self.command("PING", expect="PONG") == "PONG"
        except TransportError:
            return False
