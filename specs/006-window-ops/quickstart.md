# Quickstart: Window ops

Chinese companion: [`quickstart.zh-CN.md`](./quickstart.zh-CN.md).

## Prerequisites

- Windows desktop
- `uv sync --extra dev`
- ESP32-S3 available if constructing full `NGE2` (same as other smokes)
- YOLO model path as required by current `NGE2` construct defaults

## Unit (CI)

```powershell
uv run pytest tests/unit/test_window_ops.py -q
```

Expect green without a real interactive window (fakes).

## Hardware smoke

Edit `TITLE_QUERY`, optional `HWND`, and flags in `examples/window_smoke.py`, then:

```powershell
uv run python examples/window_smoke.py
```

Expected: prints matching windows; optionally activates / sets topmost / moves the first match or bound window; bound hwnd unchanged after find with explicit ops.

## Contract reference

See [contracts/public-api.md](./contracts/public-api.md).
