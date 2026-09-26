# Quickstart Validation: nge2 MVP Core Engine

**Feature**: `001-nge2-mvp` | **Date**: 2026-09-26

Chinese companion: [`quickstart.zh-CN.md`](./quickstart.zh-CN.md).

Validate the MVP end-to-end after implementation. See [public-api.md](./contracts/public-api.md) and [hid-protocol.md](./contracts/hid-protocol.md) for contracts; [data-model.md](./data-model.md) for entities.

## Prerequisites

- Windows, Python 3.11+
- ESP32-S3 HID device flashed with compatible firmware (for hardware path)
- Writable folder for `resource_dir` (may be empty in MVP)

## Setup

```powershell
cd <repo-root>
uv sync --extra dev
```

## Automated validation (CI / no hardware)

```powershell
uv run pytest -q
```

**Expected**: All default tests pass (mocked serial/capture). No physical device required.

Suggested coverage to include in the suite (implement phase):

- construct rejects `control_mode` 0/1
- construct rejects missing/busy HID when using real registry mocks
- keymap unknown key fails before send
- geom path length / instantaneous move when `humanize=False`
- stubs raise `NotImplementedError`
- `release` then `grab` recreates backend (fake capture)

## Manual hardware validation

1. Plug ESP32-S3; confirm OS sees a serial port.
2. Run a minimal script (illustrative):

```python
import nge2

with nge2.NGE2(resource_dir=".", capture="dxcam", humanize=True) as engine:
    frame = engine.capture.grab()
    assert frame.ndim == 3 and frame.shape[2] == 3
    engine.control.move(100, 100, duration=0.2, spread=5)
    engine.control.left_click()
    engine.control.key_click("a")
```

**Expected**:

- Construct succeeds only if device found
- Frame is BGR array
- Pointer moves / click / key observed on the host as HID input
- Leaving `with` releases serial (second construct can acquire device again)

3. Negative checks:

- Unplug device → construct fails clearly
- Hold one engine open → second `NGE2(...)` fails with busy error
- `control_mode=0` → construct fails not-implemented

## Optional screen-only check

```python
# If HID unavailable, construction fails by design in MVP (mode 2 default).
# For capture-only experiments during bring-up, use tests with injected fakes—
# product MVP still requires HID for a real NGE2(control_mode=2).
```

## Done when

- [ ] `uv run pytest` green on clean CI agent
- [ ] Manual script above succeeds with real ESP32-S3
- [ ] Busy-port and mode-0/1 failures observed as specified
