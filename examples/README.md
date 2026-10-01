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

## Drag

Edit constants in `examples/drag_smoke.py` (`DRAGS`, `HWND`, `BUTTON`, …), then:

```powershell
uv run python examples/drag_smoke.py
```

## Control gestures (library)

After `002-control-gestures`, `engine.control` also supports:

- `drag(x1, y1, x2, y2, button="L")`
- `scroll("up"|"down", notches=1)`
- `double_click(x=None, y=None, ...)` (left only; same point, no spread)
- `hotkey(*keys)` (alias of `key_click(*keys)`)

Covered by `tests/contract/test_control_gestures.py` (no hardware). Hardware: `examples/drag_smoke.py`.

## Logging

Edit constants in `examples/log_smoke.py` (`LOG_DIR`, `HWND`, `ERROR_MESSAGE`, …), then:

```powershell
uv run python examples/log_smoke.py
```

Writes `{LOG_DIR}/{YYYY-MM-DD}/nge-NNN.log` and on ERROR a JPEG under `screenshot/`.
Still needs ESP32-S3 for `NGE2` construct.

## Window find / activate / topmost / move

Edit constants in `examples/window_smoke.py` (`TITLE_QUERY`, `HWND`, `DO_*`, …), then:

```powershell
uv run python examples/window_smoke.py
```

Lists visible top-level windows matching a title substring, then optionally
activates / pins / moves the first match (or the bound hwnd). Needs ESP32-S3 for
`NGE2` construct. Library tests: `tests/unit/test_window_ops.py` (fakes, no desktop).

## Find image / color

Edit constants in `examples/find_smoke.py` (`TEMPLATE_REGION`, `HWND`, …), then:

```powershell
uv run python examples/find_smoke.py
```

Grabs the screen, saves a crop as a self-template under `resource_dir`, then runs
`find_image` / `find_images` (and optional `find_color`). Needs ESP32-S3 for construct.
Library tests: `tests/unit/test_find.py` (FakeCapture, no hardware).

### Find image with wait/poll

```powershell
uv run python examples/find_wait_smoke.py
```

Same self-template flow, but calls `find_image(..., timeout_ms=..., interval_ms=...)`.
Edit `TIMEOUT_MS` / `INTERVAL_MS` in the script. Library: `tests/unit/test_vision_wait.py`.

## OCR find_text (wait/poll)

```powershell
uv run python examples/find_text_smoke.py
```

Edit `TEXT`, `REGION`, `MULTI`, `TIMEOUT_MS` (default poll 5s), `INTERVAL_MS` (default 1000).
Returns first `OcrLine` or `None` (`multi=True` → list). Needs ESP32-S3 + YOLO model path for construct.

## YOLO / OCR (one-shot)

- **OCR**: RapidOCR (default models; no det/rec paths). Optional `ocr_kwargs`.
- **YOLO**: place ONNX under `examples/models/` (placeholder stub included; replace with real YOLOv8-detect export).

```powershell
uv run python examples/yolo_smoke.py
uv run python examples/ocr_smoke.py
```

### YOLO detect with wait/poll

```powershell
uv run python examples/yolo_wait_smoke.py
```

Edit `TIMEOUT_MS` / `INTERVAL_MS`. Polls until non-empty detections or deadline (`[]` on miss).

## Time sleep / delay (no hardware)

```powershell
uv run python examples/time_smoke.py
```

Fixed and random millisecond delays via `from nge2.time import sleep`, `Time.sleep`, and
optionally `engine.time` (`USE_ENGINE=True`). Unit coverage: `tests/unit/test_time.py`.

`NGE2` loads OCR (RapidOCR) + YOLO at construct. Other smoke scripts that construct
`NGE2` need a YOLO model under their `resource_dir` (default `models/yolo.onnx`).
Point `RESOURCE_DIR` at `examples/` or copy `examples/models` into your resource root.
Wait/poll unit coverage: `tests/unit/test_vision_wait.py`.
