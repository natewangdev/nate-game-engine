"""nate-game-engine (import ``nge2``): game scripting toolkit."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from nge2._engine import NGE2

try:
    __version__ = version("nate-game-engine")
except PackageNotFoundError:  # editable / source tree without metadata
    __version__ = "0.0.0+dev"

__all__ = ["NGE2", "__version__"]
