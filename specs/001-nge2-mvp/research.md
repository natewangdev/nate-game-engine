# Research: nge2 MVP Core Engine

**Feature**: `001-nge2-mvp` | **Date**: 2026-09-26

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. Package layout & entry API

- **Decision**: Import package `nge2` under `src/nge2/`; primary type `NGE2` with `close()` and context manager; access via `engine.capture` / `engine.control` / …
- **Rationale**: Matches ratified spec (instance API, multi-instance, explicit shutdown). Aligns with constitution library-first path.
- **Alternatives considered**: Module-level `nge2.init` singleton — rejected (harder tests, conflicts with multi-instance). Keep optional later sugar only if needed.

## 2. Capture backends

- **Decision**: Exact backend from ctor (`"dxcam"` default, or `"mss"`). Fail construction if chosen backend cannot be created; no fallback. `release()` tears down; later `grab()` recreates same backend. Always first display output. Frames: BGR `numpy.ndarray`. Regions: screen physical pixels.
- **Rationale**: Spec clarifications + prior toolkit experience (`dxcam` primary, `mss` alternate). Strict backend choice avoids silent behavior drift.
- **Alternatives considered**: Auto-fallback dxcam→mss — rejected in clarify. Process-global capture singleton — rejected.

## 3. HID transport & keymap

- **Decision**: Port behavioral contract from prior `SerialTransport` (CDC line protocol, Espressif VID hint `303a`, PING/PONG on open) and `keymap` Usage ID tables into `control/_transport.py` and `control/_keymap.py`. Absolute mouse via `MA`; clicks `CLK`; keys `KD`/`KU`/`KP`; modifiers `MOD`; emergency `STOP` on close.
- **Rationale**: Existing firmware already speaks this protocol; rewriting protocol would break devices. Spec requires keymap equivalence.
- **Alternatives considered**: Relative HID mouse — incompatible with prior absolute mapping. New JSON protocol — requires firmware change (out of scope).

## 4. Humanize / geom

- **Decision**: Internal `geom` module with cubic-bezier style path generation (prior `HumanizeConfig` / `generate_path` semantics). Used only when `humanize=True`. When `False`, single instant move; ignore duration/spread.
- **Rationale**: Spec FR-009/013; proven parameters from prior toolkit.
- **Alternatives considered**: Always-on humanize — rejected. Public stable geom API — deferred/rejected for MVP.

## 5. Window & DPI

- **Decision**: On construct, set process DPI awareness (per-monitor V2 when available, else legacy `SetProcessDPIAware`). Client-relative coords via `GetClientRect` + `ClientToScreen`. Expose hwnd, title, client region through `window` facade.
- **Rationale**: Spec FR-004/010/011; physical-pixel correctness under scaling.
- **Alternatives considered**: Require caller to set DPI — error-prone. Logical pixels — fails grab/click alignment.

## 6. Logging

- **Decision**: Logger hierarchy rooted at `nge`; console + file (default `nge.log` in cwd); level from `NGE_LOG_LEVEL`.
- **Rationale**: Spec FR-012 and prior logger behavior; root name `nge` explicitly chosen by product owner (not `nge2`).
- **Alternatives considered**: Root `nge2` — rejected by owner. No file logging — rejected.

## 7. Stubs & deferred vision

- **Decision**: Ship importable `find`, `ocr`, `yolo` that raise `NotImplementedError` on capability calls. Do not add RapidOCR/ONNX YOLO deps until those features.
- **Rationale**: Clarify Option A + full-install constitution applies to **supported** MVP modules; stubs are not “supported recognition stacks.”
- **Alternatives considered**: Omit modules — conflicts with eight-module package surface. Pre-install OCR deps unused — unnecessary weight for MVP.

## 8. Dependency set (MVP full install)

- **Decision**: Base deps: `numpy`, `dxcam`, `mss`, `pyserial` (plus transitive `comtypes` as needed by dxcam). Dev: `pytest`, `ruff`.
- **Rationale**: Constitution IV full install for supported modules; each justified by capture/HID/frame types.
- **Alternatives considered**: Optional extras — superseded by constitution amendment v1.2.0.

## 9. Testing strategy

- **Decision**: Unit tests for keymap, geom, coord conversion, stub errors, ctor validation (mode 0/1, missing backend via factory injection). Contract/integration tests with fake transport + fake grabber. Mark real device/screen tests optional.
- **Rationale**: Spec FR-017 + constitution II/III.
- **Alternatives considered**: Require hardware in CI — rejected.

## 10. Port exclusivity

- **Decision**: Track open ports (or serial handles) at process level; second `NGE2(control_mode=2)` that would open the same device fails at construct with busy error.
- **Rationale**: Clarify Q5; avoids undefined dual controllers.
- **Alternatives considered**: Lazy fail on first command — weaker UX; undocumented single-engine — conflicts with multi-instance capture stories.
