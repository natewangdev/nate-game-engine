# Quickstart Validation: Control Gestures

**Feature**: `002-control-gestures` | **Date**: 2026-09-27

Chinese companion: [`quickstart.zh-CN.md`](./quickstart.zh-CN.md).

Validate after implementation. Contracts: [public-api.md](./contracts/public-api.md), [hid-protocol.md](./contracts/hid-protocol.md). Data: [data-model.md](./data-model.md).

## Prerequisites

- Windows, Python 3.11+
- Repo with `001` MVP control already present
- ESP32-S3 only for optional hardware checks

## Setup

```powershell
cd <repo-root>
uv sync --extra dev
```

## Automated validation (CI / no hardware)

```powershell
uv run pytest -q
```

**Expected**: All default tests pass, including FakeTransport coverage for:

- `drag` command order (move / BTN down / move / BTN up) for L and R
- `scroll` up/down → `WHEEL` sign and clamp; invalid notches/direction fail before send
- `double_click` → two `CLK L`; partial coords fail
- `hotkey(*keys)` matches `key_click(*keys)` command sequence

## Manual hardware validation (optional)

With a connected ESP32-S3 and constructed `NGE2`:

1. `engine.control.drag(100, 100, 400, 300)` — pointer drags with left held
2. `engine.control.scroll("down", 5)` — content scrolls down ~5 notches
3. `engine.control.double_click(200, 200)` — left double-click at target
4. `engine.control.hotkey("ctrl", "c")` — same as `key_click("ctrl", "c")`

Optional: add thin scripts under `examples/` mirroring existing smoke style (hardcoded constants).

## Done when

- Automated suite green without hardware
- Public methods match [public-api.md](./contracts/public-api.md)
- `WHEEL` used as required for scroll
