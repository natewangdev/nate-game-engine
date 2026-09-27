# Data Model: Control Gestures

**Feature**: `002-control-gestures` | **Date**: 2026-09-27

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

In-process only (no persistence). Extends the MVP `ControlSession` with gesture operations; no new long-lived entities beyond call parameters.

## Entities

### DragGesture (request)

| Field | Type | Rules |
|-------|------|-------|
| x1, y1 | float | Start; client-relative if hwnd else screen |
| x2, y2 | float | End; same coordinate space |
| button | str | `"L"` (default) or `"R"` |
| duration | float \| None | Passed to both moves when humanize on |
| spread | float | Passed to both moves when humanize on; default **10.0** |

**Lifecycle**: move(start) → button down → pause → move(end) → button up.

### WheelScroll (request)

| Field | Type | Rules |
|-------|------|-------|
| direction | str | `"up"` \| `"down"` only |
| notches | int | Must be ≥ 1 |
| delta | int | Derived: +notches or −notches, then clamp [-127, 127] |

**Lifecycle**: validate → single `WHEEL` command → done (pointer unchanged).

### DoubleClick (request)

| Field | Type | Rules |
|-------|------|-------|
| x, y | float \| None | Both set or both None |
| hold | float \| None | Per-click hold seconds; default = existing click RNG |
| interval | float \| None | Gap between clicks; default short RNG |
| duration | float \| None | Applied only if moving to target first (exact land; no spread) |

**Lifecycle**: optional exact move (`spread=0`) → CLK L → sleep(interval) → CLK L (same position).

### KeyChord (request)

| Field | Type | Rules |
|-------|------|-------|
| keys | tuple[str, ...] | Non-empty; modifiers then main key |
| hold | float \| None | Main key hold |

**Lifecycle**: shared by `key_click` and `hotkey` (identical).

## Validation summary

| Condition | Behavior |
|-----------|----------|
| scroll notches &lt; 1 or non-int | Fail before send |
| scroll direction not up/down | Fail before send |
| double_click exactly one of x/y | Fail before send |
| empty key_click/hotkey keys | Fail before send |
| unknown key name | Fail before send (existing) |

## Relationships

- All gestures use the active `ControlSession` transport and window binding from MVP.
- Drag depends on button down/up + move; double-click depends on click/CLK; scroll depends on WHEEL; hotkey aliases key_click.
