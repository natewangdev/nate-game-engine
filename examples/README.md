# Examples

Runnable smoke scripts for **manual / hardware** checks. They need a real ESP32-S3.
CI unit tests do not use these files.

## Move mouse

Edit constants at the top of `examples/move_smoke.py` (`MOVES`, `HWND`, …), then:

```powershell
# From repo root
uv sync --extra dev
uv run python examples/move_smoke.py
```

## Move and click

Edit constants in `examples/move_and_click_smoke.py` (`CLICKS`, `HWND`, …), then:

```powershell
uv run python examples/move_and_click_smoke.py
```
