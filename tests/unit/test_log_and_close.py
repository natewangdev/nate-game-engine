from __future__ import annotations

from fakes import FakeCapture, FakeTransport
from nge2._engine import NGE2
from nge2._errors import ClosedError
from nge2.log import add_file_logging, get_logger


def test_file_logging(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = add_file_logging(tmp_path, filename="nge.log")
    get_logger("t").info("hello-nge")
    assert path.exists()
    assert "hello-nge" in path.read_text(encoding="utf-8")


def test_close_and_with(tmp_path):
    with NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(port="CLOSE1"),
        enable_file_logging=False,
    ) as eng:
        eng.control.move(1, 1)
    with NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(port="CLOSE1"),
        enable_file_logging=False,
    ) as _:
        pass
    eng3 = NGE2(
        resource_dir=tmp_path,
        capture_factory=lambda b: FakeCapture(b),
        transport_factory=lambda: FakeTransport(port="CLOSE2"),
        enable_file_logging=False,
    )
    eng3.close()
    with __import__("pytest").raises(ClosedError):
        _ = eng3.control
