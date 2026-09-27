# Contract: ESP32-S3 HID Serial Line Protocol

**Feature**: `001-nge2-mvp` | **Date**: 2026-09-26

Chinese companion: [`hid-protocol.zh-CN.md`](./hid-protocol.zh-CN.md).

Behavioral contract for USB CDC transport to ESP32-S3 HID firmware (compatible with prior nge toolkit).

## Transport

- Medium: USB CDC serial (pyserial)
- Framing: one ASCII command line per write, terminated by `\n`
- Reply: single line acknowledgement; expect `OK` unless noted
- Open settle: brief delay + input buffer reset
- Discovery hint: Espressif VID fragment `303a` in port hwid (override/explicit port optional later; MVP auto-discover)

## Commands (host → device)

| Command | Form | Expect | Meaning |
|---------|------|--------|---------|
| PING | `PING` | `PONG` | Liveness |
| MA | `MA <x> <y>` | `OK` | Absolute mouse move; device coords 0..32767 |
| CLK | `CLK <L\|R> <hold_ms>` | `OK` | Click button with hold milliseconds |
| BTN | `BTN <L\|R> <0\|1>` | `OK` | Button up (`0`) / down (`1`); required for public left/right_down/up |
| KD | `KD <usage_id>` | `OK` | Key down |
| KU | `KU <usage_id>` | `OK` | Key up |
| KP | `KP <usage_id> <hold_ms>` | `OK` | Key press |
| MOD | `MOD <bitmask>` | `OK` | Modifier state |
| STOP | `STOP` | `OK` | Release inputs / safe stop |
| WHEEL | `WHEEL <delta>` | `OK` | Optional; not required by MVP FR list |

## Mapping rules

- Pixel → device: scale primary screen size to 0..32767 (same approach as prior controller)
- Key names → Usage IDs: USB HID Keyboard/Keypad page 0x07 table equivalent to prior `keymap.KEYS` / `MODIFIERS`
- Errors: empty reply / `ERR` / unexpected → transport error; do not leave partial key/button state undocumented—prefer STOP on close (MUST release held mouse buttons and keys)

## Host responsibilities

- Ping (or equivalent) before declaring construct success for mode 2
- Exclusive port ownership while engine active
- On `close()`: attempt STOP then close serial
