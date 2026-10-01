# Research: Time module

**Feature**: `008-time`

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| API surface | Module functions + `@staticmethod` on `Time` + `engine.time` facade | Spec FR-005; window lacks true module export — time is the first full three-surface domain |
| Engine wiring | `self.time = Time()` at construct; not gated by `_ensure_open`; not closed in `close()` | Stateless; usable after close via same object or import |
| Validation | Coerce via `int(...)` only when value is already `int` bool-excluded; reject `bool`, `float`, str → `ValueError` | Spec: integer ms; bool is subclass of int — reject explicitly |
| Random | `random.randint(min_ms, max_ms)` behind `_randint` seam | Stdlib closed inclusive interval |
| Sleep | `time.sleep(ms / 1000.0)` behind `_sleep` seam | Testable without real waits |
| Alias | `delay = sleep` at module level; `Time.delay = sleep` static | Identical object or thin wrappers calling shared impl |
| Errors | `ValueError` only | Spec A; no desktop I/O domain error type |
| Constitution | Add `time` to package domain list | Spec assumption |

## Alternatives rejected

- New `TimeError` — unnecessary for pure validation.
- Float ms — inconsistent with project `*_ms: int` conventions.
- Gaussian jitter — out of scope (humanize stays in control/geom).
