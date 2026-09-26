# Nate Game Engine

Python package for game scripting (**import name**: `nge2`).

PyPI name: `nate-game-engine`.

## Features (MVP)

- Instance API: `engine = nge2.NGE2(...)`
- Screen capture (`dxcam` / `mss`)
- Hardware HID control via ESP32-S3
- Window client-area coordinates (DPI-aware)
- Logging under root name `nge`
- Stubs: `find`, `ocr`, `yolo` (NotImplementedError)

Managed with Spec Kit — see `specs/001-nge2-mvp/`.

## Prerequisites

- Windows, Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- ESP32-S3 with compatible HID firmware (for real control)

## Quick start

```powershell
uv sync --extra dev
uv run pytest -q
```

```python
import nge2

with nge2.NGE2(resource_dir=".", capture="dxcam") as engine:
    frame = engine.capture.grab()
    engine.control.move(100, 100)
    engine.control.left_click()
```

### Hardware smoke (mouse move)

Requires ESP32-S3. See `examples/README.md`.

```powershell
uv run python examples/move_smoke.py
uv run python examples/move_smoke.py --x 800 --y 450 --duration 0.4
uv run python examples/move_smoke.py --hwnd 0xYOURHWND --x 100 --y 100 --click
```

Validation details: `specs/001-nge2-mvp/quickstart.md`.

## License

MIT
