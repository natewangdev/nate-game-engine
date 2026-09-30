# Feature Specification: Vision wait/poll — OCR find_text, find_image timeout, YOLO detect timeout

**Feature Branch**: `007-vision-wait`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "OCR: find specific text in a region with multi/single return and max search time; find_image: max find time + interval; YOLO detect: max time + interval until non-empty."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

**Extends**: `004-find-vision` (`find_image`), `005-ocr-yolo-onnx` (`recognize` / `detect`). Existing one-shot APIs remain; this feature adds `find_text` and optional wait/poll parameters. After this feature lands, wait/poll behavior defined here is authoritative for those APIs.

## Clarifications (locked)

### Session 2026-10-01

| Topic | Decision |
|-------|----------|
| OCR API | **B**: New `find_text`; case-insensitive substring match; `recognize` unchanged |
| OCR returns | **A**: `OcrLine`; `multi=False` → `OcrLine \| None`; `multi=True` → `list[OcrLine]` |
| Find scope | **A**: Wait/poll params only on `find_image` (not `find_images` / `find_color`) |
| YOLO miss/timeout | **C**: Always return `list[Detection]`; timeout / no hit → `[]` (no `None`) |
| Timing | **A**: `timeout_ms` / `interval_ms`; wall-clock (includes grab+inference); `timeout_ms > 0` and `< interval_ms` → `FindError`; `timeout_ms == 0` → one attempt, ignore interval |

- Q: OCR API + match? → A: **B**
- Q: OCR return + multi? → A: **A**
- Q: Which find APIs? → A: **A** (`find_image` only)
- Q: YOLO timeout return? → A: **C** (always list; timeout → `[]`)
- Q: Time units/semantics? → A: **A** (`timeout_ms` / `interval_ms`, wall-clock, `FindError` on illegal relation)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find specific text in a region (Priority: P1)

A script author calls `engine.ocr.find_text("组队", region=...)` to locate matching OCR lines. By default they get the first matching `OcrLine` (or `None`). With `multi=True` they get all matches. Optional `timeout_ms` polls until a match appears or time runs out.

**Why this priority**: Primary new capability for UI-text driven scripting.

**Independent Test**: Fake OCR lines + FakeCapture; assert substring match, multi/single, timeout once vs poll, illegal timeout.

**Acceptance Scenarios**:

1. **Given** a region containing an OCR line with text including `"组队"`, **When** `find_text("组队")` runs with defaults, **Then** the first matching `OcrLine` is returned (move-aligned coords).
2. **Given** multiple matching lines, **When** `multi=False`, **Then** only the first match (stable order: same as `recognize` score-desc among matches, or first in filtered recognize order as documented) is returned.
3. **Given** multiple matching lines, **When** `multi=True`, **Then** a `list[OcrLine]` of all matches is returned.
4. **Given** no matching text, **When** `timeout_ms=0` and `multi=False`, **Then** `None` is returned; when `multi=True`, **Then** `[]`.
5. **Given** text appears within `timeout_ms > 0`, **When** polling with `interval_ms`, **Then** the call returns as soon as a match is found (does not wait out the full timeout).
6. **Given** no match for the full `timeout_ms > 0`, **When** the deadline passes, **Then** `multi=False` → `None`; `multi=True` → `[]`.
7. **Given** `timeout_ms > 0` and `timeout_ms < interval_ms`, **When** `find_text` is called, **Then** `FindError` is raised before polling.

---

### User Story 2 - Poll find_image until match or timeout (Priority: P1)

A script author passes `timeout_ms` / `interval_ms` to `find_image`. Zero timeout keeps today’s one-shot behavior. Positive timeout retries until a match or deadline; miss → `None`.

**Why this priority**: Common bot pattern; extends the most-used find API.

**Independent Test**: Fake find that fails then succeeds; assert early return, timeout `None`, defaults, illegal relation.

**Acceptance Scenarios**:

1. **Given** `timeout_ms=0`, **When** `find_image` runs, **Then** exactly one search attempt occurs (interval ignored); hit → `Match`, miss → `None` (unchanged).
2. **Given** `timeout_ms > 0` and a match appears on a later attempt within the budget, **When** `find_image` polls, **Then** it returns that `Match` immediately.
3. **Given** no match within `timeout_ms > 0`, **When** polling ends, **Then** `None` is returned.
4. **Given** `timeout_ms > 0` and `timeout_ms < interval_ms`, **When** called, **Then** `FindError`.

---

### User Story 3 - Poll YOLO detect until non-empty or timeout (Priority: P2)

A script author passes `timeout_ms` / `interval_ms` to `detect`. Zero timeout is one-shot (miss → `[]`). Positive timeout keeps detecting until a non-empty filtered result or deadline (timeout still → `[]`).

**Why this priority**: Same wait pattern for detection; secondary to text/image find for many scripts.

**Independent Test**: Fake detect empty then non-empty; assert early return, timeout `[]`, no `None`.

**Acceptance Scenarios**:

1. **Given** `timeout_ms=0`, **When** `detect` runs, **Then** one attempt; empty → `[]`; non-empty → that list (existing filters apply).
2. **Given** `timeout_ms > 0` and a later attempt yields detections, **When** polling, **Then** that non-empty list is returned immediately.
3. **Given** all attempts empty until deadline, **When** `timeout_ms > 0` expires, **Then** `[]` is returned (not `None`).
4. **Given** illegal `timeout_ms` / `interval_ms` relation, **When** called, **Then** `FindError`.

---

### Edge Cases

- Blank / whitespace-only `find_text` query → `FindError` (or `WindowError`-style clear error; prefer **`FindError`** for vision consistency).
- Each poll iteration MUST use a **fresh** `capture.grab` (same as existing find/ocr/yolo).
- Wall-clock budget includes grab + inference + sleep; after an attempt, if elapsed ≥ `timeout_ms`, stop without another sleep when already past deadline.
- `interval_ms` MUST be `> 0` when `timeout_ms > 0`; if `interval_ms <= 0` with positive timeout → `FindError`.
- Closed engine → `ClosedError` as today.
- `find_images` / `find_color` / `recognize` signatures unchanged in this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `engine.ocr` MUST provide `find_text(text, *, region=None, multi=False, timeout_ms=0, interval_ms=1000, ...)` matching OCR lines whose `text` **casefold-contains** the query substring. `recognize` MUST remain unchanged in behavior for existing callers.
- **FR-002**: With `multi=False`, `find_text` MUST return `OcrLine | None`. With `multi=True`, MUST return `list[OcrLine]` (empty if none). Match ordering MUST be deterministic (document: filter from score-descending `recognize` results, preserving that order).
- **FR-003**: `find_image` MUST accept `timeout_ms: int = 0` and `interval_ms: int = 500`. `timeout_ms == 0` → single attempt. `timeout_ms > 0` → poll until `Match` or deadline; deadline miss → `None`.
- **FR-004**: `detect` MUST accept `timeout_ms: int = 0` and `interval_ms: int = 500`. `timeout_ms == 0` → single attempt. `timeout_ms > 0` → poll until non-empty `list[Detection]` (after existing conf/class filters) or deadline; deadline miss → `[]` (never `None` from timeout alone).
- **FR-005**: For all three APIs, when `timeout_ms > 0` and `timeout_ms < interval_ms`, MUST raise **`FindError`**. When `timeout_ms == 0`, MUST NOT require or apply interval sleeping.
- **FR-006**: Timing MUST use **wall-clock milliseconds**; each attempt includes a fresh grab + inference/match; sleep `interval_ms` between attempts only when time remains before deadline.
- **FR-007**: Coordinates and `region` rules MUST match existing move-aligned vision conventions (hwnd → client-relative; else screen).
- **FR-008**: Automated tests MUST cover match/filter, one-shot defaults, early success under timeout, deadline miss returns, and illegal timeout/interval — with fakes (no real desktop/GPU required).

### Key Entities

- **OcrLine / Match / Detection**: Unchanged value types from 004/005.
- **Wait budget**: `timeout_ms` + `interval_ms` controlling poll loops shared conceptually across OCR/find/YOLO.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Script author can wait for on-screen text `"组队"` and receive a move-aligned `OcrLine` (or `None`/`[]`) without manual sleep loops.
- **SC-002**: Script author can poll `find_image` with a timeout and get early `Match` or `None` without changing `find_images` / `find_color`.
- **SC-003**: Script author can poll `detect` until objects appear; timeout yields `[]`, preserving list-only return type.
- **SC-004**: Illegal `timeout_ms < interval_ms` fails fast with `FindError` in 100% of automated negative tests.
- **SC-005**: CI unit tests for all three poll paths pass with fakes (no hardware).

## Assumptions

- Parameter names `timeout_ms` / `interval_ms` are the public names (milliseconds, ints).
- Default intervals: OCR find_text `1000`; find_image and detect `500`.
- Optional `min_score` on `find_text` MAY mirror `recognize` if already present; not required by this feature unless needed for parity.
- Shared internal poll helper is an implementation detail.

## Out of Scope

- Wait/poll on `find_images`, `find_color`, or `recognize`.
- Changing YOLO timeout to return `None`.
- Regex text matching; exact-only match mode.
- Async/callback APIs.
- Non-Windows platforms.
