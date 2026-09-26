# Examples

Runnable smoke scripts for **manual / hardware** checks. They need a real ESP32-S3.
CI unit tests do not use these files.

## Move mouse

```powershell
# From repo root
uv sync --extra dev

# Default: move to screen (400, 300) with humanize
uv run python examples/move_smoke.py

# Custom target
uv run python examples/move_smoke.py --x 800 --y 450 --duration 0.4 --spread 5

# Instant jump (no humanize)
uv run python examples/move_smoke.py --no-humanize --x 500 --y 500

# Client-relative (pass hwnd from WinSpy++ / Window Detective)
uv run python examples/move_smoke.py --hwnd 0x12345 --x 100 --y 100 --click
```

In Cursor/VS Code: open `examples/move_smoke.py` → Run Python File, or configure
a launch config with `args`.
