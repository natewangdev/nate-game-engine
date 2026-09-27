# Tasks: Control Gestures

**Input**: Design documents from `/specs/002-control-gestures/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — spec FR-009 / SC-005 and constitution require mocked HID coverage.

**Organization**: Tasks grouped by user story for independent implementation and testing.

Chinese companion (human-readable only): [`tasks.zh-CN.md`](./tasks.zh-CN.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: User story label (`[US1]`…`[US4]`)
- Descriptions include exact file paths

## Path Conventions

- Library: `src/nge2/`, tests: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature docs and MVP control surface exist (incremental feature; no new package layout)

- [x] T001 Verify `src/nge2/control/__init__.py` exposes `move`, `_button` / left-right down-up, `move_and_click`, `key_click` required by gestures (read-only check; no code change unless missing)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared validation helpers used by scroll/double_click — MUST complete before story APIs

**⚠️ CRITICAL**: No user story implementation begins until this phase is complete

- [x] T002 Add shared control validation helpers (e.g. require both-or-neither coords; positive int notches) in `src/nge2/control/__init__.py` raising `ControlError` before transport send

**Checkpoint**: Foundation ready — story implementation can begin

---

## Phase 3: User Story 1 — Drag (Priority: P1) 🎯 MVP

**Goal**: `drag(x1,y1,x2,y2, button="L"| "R", duration, spread)` = move → BTN down → pause → move → BTN up

**Independent Test**: FakeTransport shows MA/BTN/MA/BTN order for L and R; humanize=False yields single MA per leg

### Tests for User Story 1

- [x] T003 [P] [US1] Add drag contract tests (L/R, humanize off) in `tests/contract/test_control_gestures.py`

### Implementation for User Story 1

- [x] T004 [US1] Implement `Control.drag` in `src/nge2/control/__init__.py` per `contracts/public-api.md` and research (reuse `move` + `_button`; short pause after down)

**Checkpoint**: US1 independently testable with FakeTransport

---

## Phase 4: User Story 2 — Scroll (Priority: P1)

**Goal**: `scroll(direction, notches=1)` → one `WHEEL ±n` clamped to [-127, 127]; invalid args fail before send

**Independent Test**: FakeTransport records `WHEEL`; up/down sign; clamp; bad notches/direction raise without new commands

### Tests for User Story 2

- [x] T005 [P] [US2] Add scroll contract tests (up/down, clamp, invalid) in `tests/contract/test_control_gestures.py`

### Implementation for User Story 2

- [x] T006 [US2] Implement `Control.scroll` in `src/nge2/control/__init__.py` (`WHEEL` required; legacy nge mapping)

**Checkpoint**: US2 independently testable

---

## Phase 5: User Story 3 — Double-click (Priority: P2)

**Goal**: Left-only `double_click`; optional move; two `CLK L`; interval/hold defaults

**Independent Test**: Two `CLK L` on FakeTransport; partial x/y fails; optional pre-move

### Tests for User Story 3

- [x] T007 [P] [US3] Add double_click contract tests in `tests/contract/test_control_gestures.py`

### Implementation for User Story 3

- [x] T008 [US3] Implement `Control.double_click` in `src/nge2/control/__init__.py` (left only; both coords or neither; exact land `spread=0`; no spread param)

**Checkpoint**: US3 independently testable

---

## Phase 6: User Story 4 — Hotkey alias (Priority: P3)

**Goal**: `hotkey(*keys)` identical to `key_click(*keys)`; document `*keys` only

**Independent Test**: Same command sequence for hotkey vs key_click on FakeTransport

### Tests for User Story 4

- [x] T009 [P] [US4] Add hotkey/key_click parity tests in `tests/contract/test_control_gestures.py`

### Implementation for User Story 4

- [x] T010 [US4] Implement `Control.hotkey` as alias of `key_click` in `src/nge2/control/__init__.py`

**Checkpoint**: All stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Docs and full suite green

- [x] T011 [P] Note gesture APIs in `examples/README.md` (and optional thin smoke if useful)
- [x] T012 Run `uv run pytest -q` per `specs/002-control-gestures/quickstart.md` and fix failures until green
- [x] T013 Mark completed tasks in `specs/002-control-gestures/tasks.md` (+ sync `tasks.zh-CN.md` overview)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup** → **Foundational** → **US1 / US2 / US3 / US4** (US2–US4 can follow US1 sequentially on same file `control/__init__.py`)
- **Polish** after desired stories

### User Story Dependencies

- Stories are logically independent but share `src/nge2/control/__init__.py` and `tests/contract/test_control_gestures.py` — prefer sequential US1→US2→US3→US4 for one agent

### Parallel Opportunities

- T003/T005/T007/T009 test cases can be authored together in one file before implementations
- T011 docs parallel to T012 once code green

---

## Parallel Example: Tests first

```text
T003 drag tests
T005 scroll tests
T007 double_click tests
T009 hotkey tests
# then T004 → T006 → T008 → T010 in control/__init__.py
```

---

## Implementation Strategy

### MVP First

1. T001–T002 → T003–T004 (drag only) → validate
2. Add scroll → double_click → hotkey → polish

### Notes

- Exact checkbox format required for `/speckit-implement`
- Agents execute English `tasks.md` only
