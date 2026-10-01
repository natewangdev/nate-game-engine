# Feature Specification: Time module — sleep / delay (fixed and random ms)

**Feature Branch**: `008-time`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "Add a time module with delay supporting one-arg fixed delay and two-arg (min, max) random delay in milliseconds; callable via engine.time… and as static/import; suggest other game-script time APIs."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

**New domain**: Introduces package domain `time` (alongside `capture`, `control`, `ocr`, `yolo`, `find`, `log`, `geom`, `window`). No hardware / COM / desktop dependency. After this feature lands, behavior defined here is authoritative for the public sleep/delay APIs.

## Clarifications (locked)

### Session 2026-10-01

| Topic | Decision |
|-------|----------|
| API name & signature | **B**: Primary name **`sleep`**; one arg = fixed ms; two args `(min_ms, max_ms)` = random ms; optional **`delay`** alias with identical behavior |
| Scope this feature | **B**: Only `sleep` (+ `delay` alias); other time tools deferred |
| Random + call surfaces | **C**: Uniform closed interval `[min_ms, max_ms]`; `min > max` or negative → clear error; `from nge2.time import sleep` / `Time.sleep` / `engine.time.sleep` equivalent; no instance state |
| Return & errors | **A**: Success returns actual slept duration as **`int` ms**; illegal args → **`ValueError`** (no new `TimeError`) |

- Q: Sleep naming and fixed vs random signature? → A: **B** (`sleep`; 1-arg fixed / 2-arg random; optional `delay` alias)
- Q: Which time tools in this feature? → A: **B** (only `sleep` + `delay`)
- Q: Random distribution and call surfaces? → A: **C** (uniform closed interval; three-way equivalent; no state)
- Q: Return value and error type? → A: **A** (return actual `int` ms; `ValueError` on illegal args)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fixed millisecond delay (Priority: P1)

A script author pauses between actions with a known wait, e.g. `engine.time.sleep(500)` or `from nge2.time import sleep; sleep(500)`, and continues after that many milliseconds. The call returns the duration that was applied (`500`).

**Why this priority**: Fixed pacing is the basic building block for scripted game flows.

**Independent Test**: Fake/patched sleep seam; assert requested duration, return value, and that zero duration returns immediately with `0`.

**Acceptance Scenarios**:

1. **Given** a valid non-negative integer `ms`, **When** `sleep(ms)` is called via any of the three surfaces, **Then** the script waits approximately `ms` milliseconds and the call returns `ms` as `int`.
2. **Given** `ms == 0`, **When** `sleep(0)` is called, **Then** it returns `0` without a meaningful wait.
3. **Given** the same args, **When** calling `delay(ms)` instead of `sleep(ms)`, **Then** behavior and return value are identical.

---

### User Story 2 - Random delay in a closed range (Priority: P1)

A script author reduces robotic timing by sleeping a random duration between min and max inclusive, e.g. `engine.time.sleep(200, 800)`, and may log the returned actual milliseconds.

**Why this priority**: Primary anti-pattern for fixed-interval bots; user-requested alongside fixed delay.

**Independent Test**: Seeded or stubbed RNG; assert sampled value is in `[min_ms, max_ms]`, return equals that value, and sleep seam is invoked with that duration.

**Acceptance Scenarios**:

1. **Given** `0 <= min_ms <= max_ms`, **When** `sleep(min_ms, max_ms)` runs, **Then** the actual duration `d` satisfies `min_ms <= d <= max_ms`, the call waits for `d` ms, and returns `d` as `int`.
2. **Given** `min_ms == max_ms`, **When** called, **Then** behavior matches fixed sleep of that value (return equals that value).
3. **Given** repeated calls with a wide range, **When** many samples are taken under a controllable RNG, **Then** both endpoints are achievable (closed interval).

---

### User Story 3 - Same API via engine, class, and import (Priority: P1)

A script author uses interchangeably `engine.time.sleep(...)`, `Time.sleep(...)`, and `from nge2.time import sleep` (and the same for `delay`) without differing semantics or hidden per-engine state.

**Why this priority**: User explicitly required instance and static/import call styles; mismatch would break script portability.

**Independent Test**: Call the same legal and illegal argument sets through all three surfaces; assert identical returns and errors.

**Acceptance Scenarios**:

1. **Given** identical valid args, **When** invoked via module function, `Time` static/class method, and `engine.time`, **Then** return values and wait duration are equivalent.
2. **Given** identical illegal args, **When** invoked via any surface, **Then** the same `ValueError` condition is raised (message MAY differ in wording but MUST indicate the invalid arguments).
3. **Given** two engine instances, **When** calling `engine.time.sleep` on each, **Then** behavior does not depend on per-instance mutable time state (stateless facade).

---

### Edge Cases

- Negative `ms`, or negative `min_ms` / `max_ms` → `ValueError` before sleeping.
- `min_ms > max_ms` → `ValueError` before sleeping.
- Non-integer durations (e.g. `1.5`, non-numeric types) → `ValueError` (durations are integer milliseconds).
- Very large but valid non-negative integers: MUST be accepted by validation; practical OS sleep limits are out of scope for this spec’s success criteria.
- `KeyboardInterrupt` / process kill during sleep: behaves as the underlying sleep primitive (no special catch-and-swallow requirement).
- Closed engine: `sleep` / `delay` MUST still be usable via import / `Time` without an engine; if exposed on a closed engine facade, MUST NOT require an open engine (no desktop I/O). Prefer documenting that time APIs do not depend on engine open state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The library MUST provide a `time` domain with primary API **`sleep`**. One argument `sleep(ms)` MUST sleep a fixed `ms` milliseconds. Two arguments `sleep(min_ms, max_ms)` MUST sleep a duration drawn uniformly from the **closed integer interval** `[min_ms, max_ms]`.
- **FR-002**: **`delay`** MUST be provided as an alias of `sleep` with the same signature, semantics, and return value.
- **FR-003**: All duration arguments MUST be non-negative **integers** representing milliseconds. Validation failures (negative, `min_ms > max_ms`, non-integer / wrong type) MUST raise **`ValueError`** before any sleep occurs.
- **FR-004**: On success, `sleep` / `delay` MUST return the **actual** slept duration as **`int`** (fixed: the given `ms`; random: the sampled value).
- **FR-005**: Call surfaces MUST be behaviorally equivalent: module-level `from nge2.time import sleep` (and `delay`), class/static `Time.sleep` / `Time.delay`, and `engine.time.sleep` / `engine.time.delay`. There MUST be **no** per-instance time state that changes outcomes.
- **FR-006**: This feature’s public time surface MUST be limited to `sleep` and `delay`. Other suggested tools (`monotonic_ms`, `now_ms`, `Stopwatch`, `wait_until`, wall-clock alarms) are **out of scope**.
- **FR-007**: Automated tests MUST cover fixed delay, random range (including `min == max` and endpoint inclusivity under controllable RNG), alias parity, three call surfaces, and illegal-argument `ValueError` — without requiring real desktop hardware.

### Key Entities

- **Duration (ms)**: Non-negative integer milliseconds used as input and as the success return value.
- **Random delay sample**: Single integer drawn uniformly from `[min_ms, max_ms]` inclusive.
- **Time facade**: Stateless access path on `engine.time` mirroring module/`Time` APIs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A script author can pause a fixed number of milliseconds with one call and receive that same integer back as confirmation.
- **SC-002**: A script author can request a random pause between two inclusive millisecond bounds and receive the actual sampled duration for logging or assertions.
- **SC-003**: The same delay call works the same way whether imported, invoked on `Time`, or via `engine.time`.
- **SC-004**: Invalid durations (negative, inverted range, non-integer) fail immediately with a clear `ValueError` and do not sleep.
- **SC-005**: Unit/CI tests for the above pass without a physical game window or HID device.

## Assumptions

- Integer milliseconds match existing vision/`timeout_ms` conventions in the project.
- Optional `delay` alias satisfies authors who prefer that name while keeping `sleep` as the primary documented name.
- Uniform discrete sampling over inclusive integer endpoints is sufficient; no Gaussian / humanize distribution in this feature.
- Constitution domain list will include `time` when this feature is planned/implemented (documentation sync).

## Out of Scope

- `monotonic_ms`, wall-clock `now_ms`, `Stopwatch`, generic `wait_until`, schedule-to-wall-clock-time.
- Replacing or rewiring internal sleeps inside `control` / `geom` / vision poll helpers (those may keep private seams).
- Async / await sleep APIs.
- Guaranteeing sub-millisecond OS timer accuracy.
