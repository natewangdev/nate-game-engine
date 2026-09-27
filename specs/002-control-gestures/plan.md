# Implementation Plan: Control Gestures

**Branch**: `002-control-gestures` | **Date**: 2026-09-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-control-gestures/spec.md`

Chinese companion (human-readable only): [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Extend `nge2.control` with high-level gestures on top of the existing HID surface from `001-nge2-mvp`: `drag` (move → BTN down → move → BTN up), `scroll` (`WHEEL` with legacy nge ±1 / ±127 clamp), left-only `double_click`, and a `hotkey` alias for `key_click(*keys)`. No new runtime dependencies. Promote `WHEEL` to a required HID command in this feature’s contracts; implement and test via `FakeTransport`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Existing package deps only (`pyserial` already used by HID transport). No new runtime packages.

**Storage**: N/A

**Testing**: `pytest`; extend `tests/contract/test_control_hid.py` (and/or dedicated gesture contract tests) with `FakeTransport`; optional manual smoke under `examples/`

**Target Platform**: Windows (primary); HID firmware compatible with prior nge line protocol

**Project Type**: Python library incremental feature on `src/nge2/control`

**Performance Goals**: Gesture APIs complete within humanize/move timing already used by MVP; scroll is a single command

**Constraints**: Same coordinate/humanize/hwnd rules as `move`; left double-click only; chords via `*keys` only; wheel clamp [-127, 127]

**Scale/Scope**: Additive methods on `Control` facade; contract docs + tests + optional examples; no package layout redesign

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| I. Library-First under `src/nge2/` | PASS | Public methods on `engine.control` |
| II. Side-effect isolation | PASS | Gestures call existing transport; CI uses FakeTransport |
| III. Test discipline | PASS | Contract tests for command sequences required |
| IV. Full default install & YAGNI | PASS | No new deps; compose existing BTN/CLK/WHEEL/key_click |
| V. SemVer / Windows stated | PASS | Additive public API (minor when versioned); Windows-first |
| VI–VII. Bilingual artifacts | PASS | plan/research/data-model/contracts/quickstart EN+zh-CN |

**Post-design re-check**: PASS — contracts additive; geom stays internal; STOP-on-close remains the safety net for stuck buttons.

## Project Structure

### Documentation (this feature)

```text
specs/002-control-gestures/
├── plan.md
├── plan.zh-CN.md
├── research.md
├── research.zh-CN.md
├── data-model.md
├── data-model.zh-CN.md
├── quickstart.md
├── quickstart.zh-CN.md
├── contracts/
│   ├── public-api.md
│   ├── public-api.zh-CN.md
│   ├── hid-protocol.md
│   └── hid-protocol.zh-CN.md
└── tasks.md                 # (/speckit-tasks — not this command)
```

### Source Code (repository root)

```text
src/nge2/control/
├── __init__.py              # Add drag, scroll, double_click, hotkey
├── _transport.py            # Unchanged protocol helper (command already generic)
└── _keymap.py               # Unchanged; chords reuse resolve_modifiers/resolve_key

tests/contract/
└── test_control_hid.py      # Extend / split gesture cases (BTN/CLK/WHEEL/hotkey)

examples/                    # Optional smoke scripts (manual hardware)
└── (drag/scroll/double_click as needed)
```

**Structure Decision**: Keep single-package `src/nge2` layout. All behavior lands in `Control` methods composing existing `move`, `_button`, `move_and_click`/`CLK`, and `key_click`. Feature-local contracts live under `specs/002-control-gestures/contracts/` (authoritative for this feature; may supersede MVP notes for `WHEEL` required status).

## Complexity Tracking

> No constitution violations requiring justification.
