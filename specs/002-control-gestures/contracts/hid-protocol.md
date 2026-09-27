# Contract: HID Commands for Control Gestures

**Feature**: `002-control-gestures` | **Date**: 2026-09-27

Chinese companion: [`hid-protocol.zh-CN.md`](./hid-protocol.zh-CN.md).

Extends the MVP CDC line protocol. Transport framing, PING, MA, CLK, BTN, KD/KU/KP/MOD, STOP unchanged from `001-nge2-mvp`.

## Commands used by this feature

| Command | Form | Expect | Role in this feature |
|---------|------|--------|----------------------|
| MA | `MA <x> <y>` | `OK` | Drag / double-click pre-move |
| BTN | `BTN <L\|R> <0\|1>` | `OK` | Drag press/release |
| CLK | `CLK L <hold_ms>` | `OK` | Double-click (two commands) |
| WHEEL | `WHEEL <delta>` | `OK` | **Required** for `scroll` (no longer optional for this feature) |
| MOD / KP | as MVP | `OK` | `key_click` / `hotkey` chords |
| STOP | `STOP` | `OK` | close / safety release held buttons |

## Wheel mapping

- `scroll("up", n)` → `WHEEL +n` (after clamp)
- `scroll("down", n)` → `WHEEL -n` (after clamp)
- Clamp signed delta to **[-127, 127]** before send (legacy nge)
- One host call → one `WHEEL` line

## Host responsibilities

- Validate scroll/double_click/key args before writing serial
- Prefer completing drag up on success path; rely on STOP on close if interrupted
