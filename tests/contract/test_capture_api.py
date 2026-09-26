from __future__ import annotations

import pytest

from nge2._errors import CaptureError
from nge2.capture import Capture


def test_unknown_backend():
    with pytest.raises(CaptureError, match="Unknown"):
        Capture(backend="nope")
