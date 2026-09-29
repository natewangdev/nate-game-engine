# Implementation Plan: Window activate, topmost, move, find-by-title

**Branch**: `006-window-ops` | **Date**: 2026-09-29 | **Spec**: [spec.md](./spec.md)

Chinese companion: [`plan.zh-CN.md`](./plan.zh-CN.md).

**Input**: Feature specification from `specs/006-window-ops/spec.md`

## Summary

Extend `engine.window` with additive Win32-backed ops: `find_by_title` (visible top-level, case-insensitive substring), `activate`, `set_topmost(bool)`, and `move(x, y)` (outer-frame screen physical pixels, no resize). Ops default to the bound hwnd or accept an explicit hwnd; never auto-rebind. Reuse `WindowError`. No new runtime dependencies (stdlib `ctypes`).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: stdlib `ctypes` / `ctypes.wintypes` (user32); existing `nge2.window.Window`  
**Storage**: N/A  
**Testing**: pytest + monkeypatched Win32 helpers / fakes (no interactive desktop required in CI)  
**Target Platform**: Windows (primary; same as MVP)  
**Project Type**: Library incremental  
**Performance Goals**: Find enumeration completes in interactive script time on a typical desktop (<1s for dozens of windows)  
**Constraints**: Physical pixels; no hwnd rebind; outer-frame move coords are screen-absolute; activate OS refusals → `WindowError`  
**Scale/Scope**: Four public methods + `WindowMatch` type; unit tests + hardware smoke example  

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I. Library-first API | PASS | Additive `engine.window` surface |
| II. Side-effect isolation | PASS | Win32 behind Window methods; pure match filter unit-testable |
| III. Test discipline | PASS | Fake enumeration + target-resolution tests in CI |
| IV. Full install / simple | PASS | No new deps |
| V. SemVer | PASS | Additive minor/pre-1.0 |
| VI–VII. Bilingual | PASS | EN + zh-CN plan artifacts |

Post-design: unchanged PASS.

## Project Structure

### Documentation (this feature)

```text
specs/006-window-ops/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/public-api.md
└── tasks.md
```

### Source Code

```text
src/nge2/window/__init__.py   # WindowMatch; find/activate/set_topmost/move; Win32 helpers
src/nge2/_errors.py           # WindowError (existing)
tests/unit/test_window_ops.py # match rules, target resolution, move/topmost/activate fakes
examples/window_smoke.py      # manual desktop smoke
examples/README.md            # document smoke
```

## Complexity Tracking

None.
