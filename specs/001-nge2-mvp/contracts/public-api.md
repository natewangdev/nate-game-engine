# Contract: Public Python API (`nge2`)

**Feature**: `001-nge2-mvp` | **Date**: 2026-09-26

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

This is the consumer-facing library contract for MVP. Types are conceptual; exact Python typing lands in implementation.

## Package

```text
import nge2
engine = nge2.NGE2(
    resource_dir=...,          # required
    capture="dxcam",           # "dxcam" | "mss"
    hwnd=None,                 # optional int
    humanize=True,             # bool
    control_mode=2,            # 0|1 fail; 2 HID
)
```

- `nge2.__version__`: str
- Context manager: `with nge2.NGE2(...) as engine:`
- `engine.close() -> None`

## `engine.capture`

| Method | Signature (conceptual) | Notes |
|--------|------------------------|-------|
| grab | `grab(region: tuple[int,int,int,int] \| None = None) -> ndarray` | BGR; region screen physical pixels; recreates backend after release |
| release | `release() -> None` | Tear down backend |

## `engine.control`

| Method | Signature (conceptual) | Notes |
|--------|------------------------|-------|
| move | `move(x, y, duration=None, spread=10.0) -> None` | Client-relative if hwnd else screen; humanize rules per spec; default spread 10 px |
| left_click | `left_click(hold=None) -> None` | Current position; full click via `CLK` |
| right_click | `right_click(hold=None) -> None` | Current position; full click via `CLK` |
| left_down | `left_down() -> None` | Current position; press only (`BTN L 1`); no auto-up |
| left_up | `left_up() -> None` | Current position; release only (`BTN L 0`) |
| right_down | `right_down() -> None` | Current position; press only (`BTN R 1`); no auto-up |
| right_up | `right_up() -> None` | Current position; release only (`BTN R 0`) |
| move_and_click | `move_and_click(x, y, hold=None, duration=None, spread=10.0, button="L") -> None` | Default spread matches `move` |
| key_click | `key_click(key: str, ...) -> None` | Supports chords/modifiers; down→up + interval |
| key_down | `key_down(key: str) -> None` | |
| key_up | `key_up(key: str) -> None` | |

Exact chord API shape (single string `"ctrl+c"` vs `*keys`) MUST match keymap capabilities and be documented in quickstart; prefer compatibility with prior `hotkey(*keys)` / `press` semantics where practical.

## `engine.window`

| Member | Notes |
|--------|-------|
| hwnd | Bound handle or None |
| title | Window title string |
| client_region | Client visual region (document whether local and/or screen tuple) |

## `engine.log` / package logging

- Root logger name: `nge`
- Env: `NGE_LOG_LEVEL`
- File logging available (default file under cwd)

## Stubs

- `engine.find.*`, `engine.ocr.*`, `engine.yolo.*` (and/or `import nge2.find` etc.): capability calls raise `NotImplementedError`

## Errors (construct / use)

| Condition | Behavior |
|-----------|----------|
| control_mode 0 or 1 | Fail construct: not implemented |
| capture backend unavailable | Fail construct: no fallback |
| no HID device | Fail construct |
| HID port busy | Fail construct |
| closed engine used | Fail clearly |
| unknown key | Fail before send |

## Non-goals of this contract

- Stable public `geom` API
- OCR/YOLO/find behavior beyond stub errors
