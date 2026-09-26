#!/usr/bin/env python3
"""Hardware smoke test: move the mouse via ESP32-S3 HID.

Requires a connected device. Does not run in CI.

Examples (from repo root)::

    uv run python examples/move_smoke.py
    uv run python examples/move_smoke.py --x 800 --y 450 --duration 0.4
    uv run python examples/move_smoke.py --hwnd 0x12345 --x 100 --y 100 --click
    uv run python examples/move_smoke.py --no-humanize --x 500 --y 500
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_hwnd(raw: str | None) -> int | None:
    if raw is None or raw.strip() == "":
        return None
    text = raw.strip().lower()
    if text.startswith("0x"):
        return int(text, 16)
    return int(text, 10)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Move mouse with nge2 (real ESP32-S3 required).",
    )
    parser.add_argument("--x", type=float, default=400.0, help="Target X (screen or client-relative)")
    parser.add_argument("--y", type=float, default=300.0, help="Target Y (screen or client-relative)")
    parser.add_argument(
        "--duration",
        type=float,
        default=0.3,
        help="Move duration in seconds (ignored when --no-humanize)",
    )
    parser.add_argument(
        "--spread",
        type=float,
        default=0.0,
        help="Landing-point scatter radius in pixels (humanize only)",
    )
    parser.add_argument(
        "--hwnd",
        type=str,
        default=None,
        help="Window handle (decimal or 0xHEX). If set, --x/--y are client-relative.",
    )
    parser.add_argument(
        "--no-humanize",
        action="store_true",
        help="Instant jump; duration/spread ignored",
    )
    parser.add_argument(
        "--click",
        action="store_true",
        help="Left-click after move",
    )
    parser.add_argument(
        "--capture",
        choices=("dxcam", "mss"),
        default="dxcam",
        help="Capture backend used at construct (default dxcam)",
    )
    parser.add_argument(
        "--resource-dir",
        type=Path,
        default=Path("."),
        help="resource_dir for NGE2 (default: cwd)",
    )
    args = parser.parse_args(argv)

    try:
        import nge2
        from nge2._errors import ConstructError
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    hwnd = _parse_hwnd(args.hwnd)
    humanize = not args.no_humanize

    print(
        f"NGE2 move smoke: x={args.x} y={args.y} duration={args.duration} "
        f"spread={args.spread} hwnd={hwnd!r} humanize={humanize} click={args.click}"
    )

    try:
        with nge2.NGE2(
            resource_dir=args.resource_dir,
            capture=args.capture,
            hwnd=hwnd,
            humanize=humanize,
        ) as engine:
            if hwnd is not None:
                print(f"window title={engine.window.title!r}")
                print(f"client_region={engine.window.client_region}")
            engine.control.move(
                args.x,
                args.y,
                duration=None if args.no_humanize else args.duration,
                spread=0.0 if args.no_humanize else args.spread,
            )
            print("move done")
            if args.click:
                engine.control.left_click()
                print("click done")
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
