from __future__ import annotations

import pytest

from nge2.control import _port_registry as port_registry


@pytest.fixture(autouse=True)
def _clear_ports():
    port_registry.clear()
    yield
    port_registry.clear()
