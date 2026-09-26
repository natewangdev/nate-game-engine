# Implementation Plan: nge2 MVP Core Engine

**Branch**: `001-nge2-mvp` | **Date**: 2026-09-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-nge2-mvp/spec.md`

Chinese companion (human-readable only): [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Rebuild the package as importable `nge2` with an instance-centric `NGE2` facade that owns per-instance screen capture (`dxcam` or `mss`), ESP32-S3 HID control (serial line protocol), internal humanize geometry, window client-area mapping (DPI-aware), and logging. MVP implements capture + HID control + geom + window + log; ships `find`/`ocr`/`yolo` as importable stubs. Design ports behavioral contracts from the prior `nate-gaming-engine` toolkit without vendoring it.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `numpy` (BGR frames); `dxcam` + `mss` (capture backends); `pyserial` (HID CDC); stdlib `ctypes`/`logging` (Win32 window + DPI, logging). Stub modules need no OCR/YOLO runtimes in MVP.

**Storage**: N/A (in-process only; optional log file under cwd)

**Testing**: `pytest`; pure-logic unit tests; mock serial + mock capture for CI; optional manual markers for real HID/screen

**Target Platform**: Windows (primary); non-Windows out of scope

**Project Type**: Python library (`src/` layout), PyPI name `nate-game-engine`, import `nge2`

**Performance Goals**: Engine construct + full-screen grab usable within ~5s on typical desktop (excl. cold install); HID path rate aligned with prior humanize (~144 Hz target waypoint rate, not a hard SLA)

**Constraints**: Physical-pixel / DPI-aware coordinates; first-display capture only; no auto-fallback between capture backends; one HID serial holder per port; full default install (no extras)

**Scale/Scope**: Single-package MVP (~8 modules); multi-instance engines allowed with independent capture; HID exclusive per port

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| I. Library-First under `src/nge2/` | PASS | Instance API `nge2.NGE2`; scripts are consumers |
| II. Side-effect isolation | PASS | Transport/capture behind narrow interfaces; mockable; engine ctor may open declared backends only |
| III. Test discipline | PASS | pytest + mocks for CI; hardware optional |
| IV. Full default install & YAGNI | PASS | Base deps for MVP modules; no extras; no speculative layers |
| V. SemVer / Windows stated | PASS | Pre-1.0 library; Windows-first documented |
| VI–VII. Bilingual artifacts | PASS | plan/research/data-model/contracts/quickstart paired EN+zh-CN |

**Post-design re-check**: PASS — contracts describe public surface + HID protocol; geom remains internal; stubs keep package surface without implementing deferred features.

## Project Structure

### Documentation (this feature)

```text
specs/001-nge2-mvp/
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
src/nge2/
├── __init__.py              # export NGE2, __version__; package docstring
├── _engine.py               # NGE2 construction, close, context manager, module wiring
├── capture/
│   └── __init__.py          # Capture facade: grab, release; backend factory
├── control/
│   ├── __init__.py          # Control facade (HID mode)
│   ├── _transport.py        # SerialTransport, find_port, TransportError
│   └── _keymap.py           # KEYS / MODIFIERS / resolve_key
├── geom/
│   └── __init__.py          # HumanizeConfig, generate_path (not stable public)
├── window/
│   └── __init__.py          # hwnd, title, client rect helpers
├── log/
│   └── __init__.py          # root logger "nge", file + console, NGE_LOG_LEVEL
├── find/
│   └── __init__.py          # stub → NotImplementedError
├── ocr/
│   └── __init__.py          # stub → NotImplementedError
└── yolo/
    └── __init__.py          # stub → NotImplementedError

tests/
├── unit/                    # keymap, geom, coordinate math, stub errors
├── contract/                # public API signatures / NGE2 ctor validation (mocked I/O)
└── integration/             # optional @pytest.mark.hardware / screen

pyproject.toml               # name nate-game-engine; packages src/nge2; full deps
```

**Structure Decision**: Single Python library with `src/nge2` modules matching the eight public domains. HID transport/keymap live under `control/` as private helpers. Remove obsolete `src/nate_game_engine/` during implement.

## Complexity Tracking

> No constitution violations requiring justification.
