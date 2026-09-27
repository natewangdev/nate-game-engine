#!/usr/bin/env python3
"""Hardware smoke test: dated file logging + ERROR screenshot.

Requires a connected ESP32-S3 (NGE2 construct). Does not run in CI.

Edit the constants below, then from repo root::

    uv run python examples/log_smoke.py

Then check ``{LOG_DIR}/{YYYY-MM-DD}/nge-NNN.log`` and
``.../screenshot/{HHMMSS}-{xxx}.jpg``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- edit these ---
LOG_DIR = Path("logs")
HWND = 262834  # None = fullscreen ERROR shot; int = window client region
ERROR_MESSAGE = "日志冒烟测试：这是一条 ERROR，应生成带中文叠字的截图"
CAPTURE = "dxcam"  # "dxcam" | "mss"
RESOURCE_DIR = Path(".")
# ------------------


def main() -> int:
    try:
        import nge2
        from nge2._errors import ConstructError
        from nge2.log import get_logger
    except ImportError:
        print("nge2 not installed. Run: uv sync --extra dev", file=sys.stderr)
        return 2

    print(
        f"NGE2 log smoke: log_dir={LOG_DIR.resolve()} hwnd={HWND!r} "
        f"error_message={ERROR_MESSAGE!r}"
    )

    try:
        engine = nge2.NGE2(
            resource_dir=RESOURCE_DIR,
            capture=CAPTURE,
            hwnd=HWND,
            log_dir=LOG_DIR,
        )
    except ConstructError as exc:
        print(f"Construct failed: {exc}", file=sys.stderr)
        return 1

    try:
        if HWND is not None:
            print(f"window title={engine.window.title!r}")
            print(f"client_region={engine.window.client_region}")
        print(f"log_file={engine._log_path}")
        log = get_logger("smoke")
        log.info("log smoke: INFO line (no screenshot)")
        log.warning("log smoke: WARNING line (no screenshot)")
        log.error(ERROR_MESSAGE)
        day_dir = engine._log_path.parent if engine._log_path else None
        if day_dir is not None:
            log_text = engine._log_path.read_text(encoding="utf-8")
            print("--- log file tail ---")
            print("\n".join(log_text.strip().splitlines()[-5:]))
            shots = sorted((day_dir / "screenshot").glob("*.jpg"))
            print(f"screenshots ({len(shots)}):")
            for p in shots:
                print(f"  {p}")
            if not shots:
                print("WARNING: expected at least one ERROR screenshot", file=sys.stderr)
                return 1
            if "nge.smoke" in log_text or "nge.capture" in log_text:
                print("WARNING: log lines still contain module names", file=sys.stderr)
                return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.close()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
