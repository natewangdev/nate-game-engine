# Contract: Public Control Gesture APIs (`nge2.control`)

**Feature**: `002-control-gestures` | **Date**: 2026-09-27

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

Additive consumer-facing methods on `engine.control`. MVP methods (`move`, clicks, button down/up, `key_click`, …) remain as in `001-nge2-mvp` unless noted.

## New / formalized methods

| Method | Signature (conceptual) | Notes |
|--------|------------------------|-------|
| drag | `drag(x1, y1, x2, y2, *, button="L", duration=None, spread=10.0) -> None` | move→BTN down→pause→move→BTN up; `"L"`\|`"R"`; default spread matches `move` |
| scroll | `scroll(direction: str, notches: int = 1) -> None` | `direction` `"up"`\|`"down"`; notches ≥ 1; no pointer move |
| double_click | `double_click(x=None, y=None, *, hold=None, interval=None, duration=None) -> None` | Left only; both coords or neither; **no `spread`** — both clicks at the same point |
| hotkey | `hotkey(*keys: str, hold=None) -> None` | Alias of `key_click(*keys, hold=hold)` |

## Existing chord API (formalized)

| Method | Signature | Notes |
|--------|-----------|-------|
| key_click | `key_click(*keys: str, hold=None) -> None` | Official chord form; modifiers then main key; **no** `"ctrl+c"` string |

## Errors

| Condition | Behavior |
|-----------|----------|
| Invalid scroll direction | `ControlError` (or clear control error) before send |
| notches &lt; 1 | Fail before send |
| double_click with only one of x/y | Fail before send |
| empty keys for key_click/hotkey | Fail before send |
| unknown key | Fail before send (existing) |

## Non-goals

- Right/middle double-click
- Wheel tilt
- Chord string DSL
