# Research: Control Gestures

**Feature**: `002-control-gestures` | **Date**: 2026-09-27

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. Drag composition

- **Decision**: Implement `drag` as: `move(start)` → `_button(down)` → short sleep (same band as post-move click pause, ~0.02–0.06s) → `move(end)` → `_button(up)`. Use existing `left_down`/`right_down`/`left_up`/`right_up` helpers (or `_button`) so BTN commands stay consistent.
- **Rationale**: Spec requires press-move-release; MVP already has move + BTN. Avoid duplicate pixel→HID logic.
- **Alternatives considered**: Expose only docs telling authors to compose manually — rejected (SC-001). New firmware DRAG command — out of scope / firmware change.

## 2. Wheel delta (legacy nge)

- **Decision**: `scroll("up"|"down", notches=1)` sends one `WHEEL <delta>` where `delta = +notches` for up and `-notches` for down, then clamp to [-127, 127] (same as `nate-gaming-engine` `controller.wheel`). Reject non-positive notches and invalid direction before send (`ControlError`).
- **Rationale**: Product owner locked legacy behavior; firmware already expects this.
- **Alternatives considered**: ±120 Windows wheel units — rejected. Multiple WHEEL commands per notch — rejected (spec: single command with accumulated delta).

## 3. Double-click

- **Decision**: Left only. Optional move when both x,y provided; else current position. Pre-move MUST use `spread=0` (exact target). Two `CLK L` via existing click path without re-moving between clicks so both land on the same point. Interval: explicit or `rng` short gap (~40–80 ms). Fail if exactly one of x/y is set. No `spread` parameter on `double_click`.
- **Rationale**: Spec requires same-point double-click; scatter would break UI double-click targets.
- **Alternatives considered**: Default spread=10 like move — rejected by product. Two BTN down/up pairs — weaker hold control vs CLK.

## 4. Hotkey alias

- **Decision**: `hotkey(*keys, hold=None)` delegates to `key_click(*keys, hold=hold)`. Document `*keys` only; no `"ctrl+c"` parser.
- **Rationale**: Spec P3; capability exists; alias improves discoverability.
- **Alternatives considered**: New `combo()` name — redundant. String DSL — explicitly rejected.

## 5. Contract placement vs MVP

- **Decision**: Ship feature contracts under `specs/002-control-gestures/contracts/` that list additive public methods and mark `WHEEL` required. Do not rewrite all of `001` history; implement phase may also patch root-facing docs (README/examples) lightly.
- **Rationale**: Spec Kit feature isolation; agents executing this feature read this directory’s English contracts.
- **Alternatives considered**: Only edit `001` contracts — mixes shipped MVP history with new work.

## 6. Testing

- **Decision**: Extend contract tests with FakeTransport asserting command order for drag (`MA*`/`BTN`/`MA*`/`BTN`), scroll (`WHEEL`), double_click (two `CLK L`), hotkey vs key_click parity. No new pytest plugins.
- **Rationale**: Constitution II/III; SC-005.
- **Alternatives considered**: Hardware-only verification — rejected for CI.
