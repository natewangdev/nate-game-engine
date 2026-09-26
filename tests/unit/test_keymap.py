from __future__ import annotations

import pytest

from nge2.control._keymap import resolve_key, resolve_modifiers


def test_letters_and_aliases():
    assert resolve_key("a") == 0x04
    assert resolve_key("Enter") == 0x28
    assert resolve_key("esc") == resolve_key("escape")


def test_modifiers():
    assert resolve_modifiers("ctrl", "shift") == (0x01 | 0x02)


def test_unknown_key():
    with pytest.raises(KeyError, match="Unknown key"):
        resolve_key("not-a-key")
