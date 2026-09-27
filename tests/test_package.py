from importlib.metadata import version as pkg_version

from nge2 import NGE2, __version__


def test_version_and_export():
    assert __version__ == pkg_version("nate-game-engine")
    assert NGE2 is not None
