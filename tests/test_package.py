from nge2 import NGE2, __version__


def test_version_and_export():
    assert __version__ == "0.1.0"
    assert NGE2 is not None
