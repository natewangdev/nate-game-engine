# Tasks: nge2 MVP Core Engine

**Input**: Design documents from `/specs/001-nge2-mvp/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — spec FR-017 and constitution require automated CI with mocked serial/capture.

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

**Purpose**: Rebuild package layout and tooling for `nge2`

- [x] T001 Remove obsolete package tree `src/nate_game_engine/` and update imports/tests that referenced it
- [x] T002 Create `src/nge2/` module directories per plan (`capture`, `control`, `geom`, `window`, `log`, `find`, `ocr`, `yolo`) with package `__init__.py` placeholders
- [x] T003 Update `pyproject.toml` for import package `nge2`, hatch `src/nge2`, and full runtime deps `numpy`, `dxcam`, `mss`, `pyserial` (plus transitive as needed); keep `pytest`/`ruff` in `dev`
- [x] T004 [P] Create test layout `tests/unit/`, `tests/contract/`, `tests/integration/` with `__init__.py` files
- [x] T005 [P] Align `README.md` naming (Nate Game Engine / `nate-game-engine` / `import nge2`) with FR-001 without documenting unfinished APIs as done

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared engine shell, logging, stubs, and injectable I/O seams — MUST complete before user stories

**⚠️ CRITICAL**: No user story work begins until this phase is complete

- [x] T006 Implement logger root `nge`, console handler, `NGE_LOG_LEVEL`, and file helper defaulting to cwd `nge.log` in `src/nge2/log/__init__.py`
- [x] T007 [P] Implement importable stubs that raise `NotImplementedError` on capability entrypoints in `src/nge2/find/__init__.py`, `src/nge2/ocr/__init__.py`, and `src/nge2/yolo/__init__.py`
- [x] T008 Define shared errors (e.g. construct/backend/port/closed) in `src/nge2/_errors.py`
- [x] T009 Implement process-level HID port registry (open/busy/release) in `src/nge2/control/_port_registry.py` for exclusivity rules
- [x] T010 Implement `NGE2` skeleton in `src/nge2/_engine.py`: required `resource_dir` (relative→cwd), params `capture`/`hwnd`/`humanize`/`control_mode`, reject `control_mode` 0/1 immediately, `close()` + context manager flags, wire module attributes; support injectable capture/transport factories for tests
- [x] T011 Export `NGE2` and `__version__` from `src/nge2/__init__.py` per `contracts/public-api.md`
- [x] T012 [P] Add unit tests for stubs and mode-0/1 construct rejection in `tests/unit/test_stubs_and_modes.py` using fakes so no hardware is required

**Checkpoint**: Foundation ready — story implementation can begin

---

## Phase 3: User Story 1 — Construct engine and capture screen (Priority: P1) 🎯 MVP slice

**Goal**: Per-instance capture with `dxcam`/`mss`, BGR grab (full/region), release then recreate on next grab; construct fails if chosen backend unavailable (no fallback)

**Independent Test**: With mocked/fake capture (and fake HID if ctor requires mode 2), construct engine, `grab()`, regional `grab()`, `release()` then `grab()` again; assert BGR `ndarray` shapes; assert backend-unavailable construct fails

### Tests for User Story 1

- [x] T013 [P] [US1] Add unit/contract tests for capture grab/release/recreate and backend failure in `tests/unit/test_capture.py` and `tests/contract/test_capture_api.py`

### Implementation for User Story 1

- [x] T014 [US1] Implement capture backend factory (exact `"dxcam"` or `"mss"`, first display only, fail if unavailable, no fallback) in `src/nge2/capture/__init__.py` (or `src/nge2/capture/_backends.py` if split)
- [x] T015 [US1] Implement `grab(region=None) -> BGR ndarray` and `release()` with post-release recreate-on-grab in `src/nge2/capture/__init__.py`
- [x] T016 [US1] Wire per-instance `engine.capture` lifecycle into `src/nge2/_engine.py` (construct opens/validates chosen backend; `close()` releases capture)
- [x] T017 [US1] Ensure multi-instance engines do not share capture state (cover in `tests/unit/test_capture.py`)

**Checkpoint**: US1 independently testable with fakes

---

## Phase 4: User Story 2 — HID mouse/keyboard control (Priority: P1)

**Goal**: ESP32-S3 HID via serial: auto-discover, busy-port fail, move/click/keys with humanize/geom; keymap Usage IDs per prior contract

**Independent Test**: Mocked `SerialTransport` exercises move (humanize on/off), clicks with hold, move_and_click, key_down/up/click; construct fails when no device / port busy

### Tests for User Story 2

- [x] T018 [P] [US2] Add keymap unit tests (known keys, modifiers, unknown key fails before send) in `tests/unit/test_keymap.py`
- [x] T019 [P] [US2] Add geom unit tests (path waypoints when humanize; instant ignore duration/spread when not) in `tests/unit/test_geom.py`
- [x] T020 [P] [US2] Add control contract tests with fake transport (commands MA/CLK/KD/KU/KP/MOD) in `tests/contract/test_control_hid.py`

### Implementation for User Story 2

- [x] T021 [P] [US2] Port HID Usage ID tables and `resolve_key` / modifiers into `src/nge2/control/_keymap.py` per `contracts/hid-protocol.md`
- [x] T022 [P] [US2] Implement `SerialTransport`, `find_port` (VID hint `303a`), PING/PONG, command/ack errors in `src/nge2/control/_transport.py`
- [x] T023 [P] [US2] Implement `HumanizeConfig` and `generate_path` in `src/nge2/geom/__init__.py` (internal-only; not stable public export)
- [x] T024 [US2] Implement control facade `move` / `left_click` / `right_click` / `move_and_click` / `key_click` / `key_down` / `key_up` with pixel→0..32767 mapping and default hold/intervals in `src/nge2/control/__init__.py`
- [x] T025 [US2] Integrate HID open (auto-discover + ping), port registry busy fail, and `close()` STOP+release into `src/nge2/_engine.py` for `control_mode=2`
- [x] T026 [US2] When `humanize=False`, ensure `move` is instantaneous and ignores `duration`/`spread` in `src/nge2/control/__init__.py`

**Checkpoint**: US2 independently testable with fake transport

---

## Phase 5: User Story 3 — Window binding and client-relative coordinates (Priority: P2)

**Goal**: DPI-aware process; hwnd binding; client-relative moves via GetClientRect + ClientToScreen; window queries for hwnd/title/client region

**Independent Test**: Fake or real hwnd metrics unit tests for conversion; with hwnd, `move(x,y)` uses client-relative; without hwnd, screen absolute; window API returns documented geometry

### Tests for User Story 3

- [x] T027 [P] [US3] Add coordinate conversion unit tests in `tests/unit/test_window_coords.py`

### Implementation for User Story 3

- [x] T028 [US3] Implement DPI awareness helper and window queries (hwnd, title, client local/screen rects) in `src/nge2/window/__init__.py`
- [x] T029 [US3] Call DPI setup during `NGE2` construct in `src/nge2/_engine.py` (FR-004)
- [x] T030 [US3] Apply client-relative→screen conversion in `control.move` / `move_and_click` when `hwnd` set in `src/nge2/control/__init__.py`; clear errors for invalid/destroyed hwnd
- [x] T031 [US3] Expose `engine.window` API surface per `contracts/public-api.md` from `src/nge2/_engine.py`

**Checkpoint**: US3 independently testable

---

## Phase 6: User Story 4 — Logging, unimplemented modes, shutdown (Priority: P3)

**Goal**: Confirm mode 0/1 failures, file+console logging under `nge`, and `close`/`with` releasing HID+capture with post-close ops failing

**Independent Test**: Construct mode 0/1 fails; logs appear in console and `nge.log`; after `close()`, capture/control fail clearly

### Tests for User Story 4

- [x] T032 [P] [US4] Add tests for logging file+level and closed-engine errors in `tests/unit/test_log_and_close.py`

### Implementation for User Story 4

- [x] T033 [US4] Ensure construct error messages for `control_mode` 0/1 state API reserved/not implemented clearly in `src/nge2/_engine.py`
- [x] T034 [US4] Ensure `close()` / `__exit__` releases HID (STOP) and capture; further use raises closed error in `src/nge2/_engine.py`
- [x] T035 [US4] Verify default file logging path cwd `nge.log` and env level behavior documented in code docs of `src/nge2/log/__init__.py`

**Checkpoint**: All four stories independently verifiable with mocks

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Repo hygiene and quickstart validation

- [x] T036 [P] Update `tests/test_package.py` (or replace) to assert `import nge2` and `__version__`
- [x] T037 [P] Run `ruff check` / format on `src/nge2` and `tests` and fix issues
- [x] T038 Sync root `README.md` quickstart with `specs/001-nge2-mvp/quickstart.md` install/test commands
- [x] T039 Run full `uv run pytest -q` (mocked path) and fix failures until green per quickstart automated section
- [x] T040 Manual checklist note: execute hardware steps in `specs/001-nge2-mvp/quickstart.md` when ESP32-S3 available (document result in PR/notes; not required for CI green)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** → no deps
- **Phase 2 Foundational** → after Setup; **blocks** all stories
- **Phase 3 US1** → after Foundational
- **Phase 4 US2** → after Foundational; practically after US1 if sharing one `NGE2` wiring file sequentially (same `_engine.py` — prefer sequential US1 then US2 for that file)
- **Phase 5 US3** → after US2 control move exists (needs control facade)
- **Phase 6 US4** → after Foundational; best after US1+US2 close paths exist
- **Phase 7 Polish** → after desired stories

### User Story Dependencies

- **US1 (P1)**: After Foundational — capture slice
- **US2 (P1)**: After Foundational — HID/geom; coordinate hwnd mapping can stay screen-absolute until US3
- **US3 (P2)**: After US2 move API exists
- **US4 (P3)**: Overlaps foundation; finalize after US1/US2 resource lifecycle

### Parallel Opportunities

- T004/T005; T007; T018/T019/T020; T021/T022/T023; T027; T032; T036/T037 can be parallel within their phases when files differ
- Avoid parallel edits to `src/nge2/_engine.py` across stories

### Parallel Example: User Story 2

```text
T018 tests/unit/test_keymap.py
T019 tests/unit/test_geom.py
T020 tests/contract/test_control_hid.py
T021 src/nge2/control/_keymap.py
T022 src/nge2/control/_transport.py
T023 src/nge2/geom/__init__.py
# then sequential: T024 → T025 → T026
```

---

## Implementation Strategy

### MVP First (suggested)

1. Phase 1 + 2  
2. Phase 3 US1 (capture) — validate with fakes  
3. Phase 4 US2 (HID) — validate with fake transport + optional real device  
4. US3 → US4 → Polish  

### Incremental Delivery

Each story checkpoint should leave `uv run pytest` green for completed scopes.

---

## Notes

- Exact checkbox format required for `/speckit-implement`
- Do not treat `geom` as stable public API in exports
- Agents: execute English `tasks.md` only; ignore `tasks.zh-CN.md` for execution (constitution VI)

