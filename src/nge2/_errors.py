"""Shared error types for nge2."""

from __future__ import annotations


class NGEError(RuntimeError):
    """Base error for Nate Game Engine."""


class ConstructError(NGEError):
    """Raised when ``NGE2`` construction fails."""


class CaptureError(NGEError):
    """Raised when screen capture fails."""


class ControlError(NGEError):
    """Raised when HID/control operations fail."""


class ClosedError(NGEError):
    """Raised when using an engine after ``close()``."""


class WindowError(NGEError):
    """Raised when window queries or coordinate conversion fail."""
