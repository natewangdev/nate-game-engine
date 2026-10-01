# Implementation Plan: Time module (sleep / delay)

**Branch**: `008-time` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

Chinese companion: [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Add stateless `nge2.time` domain: `sleep` / `delay` with fixed (1-arg) or uniform closed-interval random (2-arg) millisecond delays; equivalent call surfaces via module import, `Time` static methods, and `engine.time`. Return actual slept `int` ms; illegal args → `ValueError`. No new dependencies. Do not rewire control/geom/vision internal sleeps.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: stdlib `time`, `random`  
**Testing**: pytest + monkeypatch `_sleep` / `_randint` seams  
**Target Platform**: Windows (stdlib only; no Win32 required for this module)  
**Project Type**: Library incremental  
**Constraints**: Integer ms; closed uniform `[min, max]`; three-way API equivalence; no per-instance state; no `TimeError`

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I–III | PASS | Library API; faked sleep/RNG tests; example smoke |
| IV | PASS | No new runtime deps |
| V–VII | PASS | Additive domain `time`; bilingual artifacts |

Post-design: still PASS. Update constitution domain list to include `time`.

## Project Structure

```text
src/nge2/time/__init__.py       # Time, sleep, delay; _sleep / _randint seams
src/nge2/_engine.py             # self.time = Time() (no close / open gate)
.specify/memory/constitution.md # add time to domain list (+ zh-CN)
tests/unit/test_time.py
examples/time_smoke.py
examples/README.md              # brief entry
```

## Complexity Tracking

None.
