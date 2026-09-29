# Tasks: Window ops

Chinese companion: [`tasks.zh-CN.md`](./tasks.zh-CN.md).

**Input**: Design docs from `specs/006-window-ops/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1: Setup

- [x] T001 Confirm feature docs present under `specs/006-window-ops/` (plan, research, data-model, contracts, quickstart)

## Phase 2: Foundational

- [x] T002 Add `WindowMatch` frozen dataclass and document target-resolution helper in `src/nge2/window/__init__.py`
- [x] T003 [P] Add monkeypatchable Win32 helpers (`_list_visible_toplevel`, `_activate_hwnd`, `_set_topmost_hwnd`, `_move_hwnd`) in `src/nge2/window/__init__.py`

## Phase 3: User Story 1 — Find by title (P1)

**Goal**: `find_by_title` returns visible top-level matches; no rebind  
**Independent test**: Monkeypatched enumeration; assert substring filter, empty list, blank → error, bound unchanged

- [x] T004 [P] [US1] Unit tests for find match / blank / empty in `tests/unit/test_window_ops.py`
- [x] T005 [US1] Implement `Window.find_by_title` in `src/nge2/window/__init__.py` per contracts/public-api.md

## Phase 4: User Story 2 — Activate (P1)

**Goal**: Activate bound or explicit hwnd; clear errors  
**Independent test**: Fake `_activate_hwnd`; missing target / failure → `WindowError`

- [x] T006 [P] [US2] Unit tests for activate target resolution and errors in `tests/unit/test_window_ops.py`
- [x] T007 [US2] Implement `Window.activate` in `src/nge2/window/__init__.py`

## Phase 5: User Story 3 — Topmost (P2)

**Goal**: `set_topmost(True|False)` without implying activate  
**Independent test**: Fake records enabled flag; missing target → `WindowError`

- [x] T008 [P] [US3] Unit tests for set_topmost in `tests/unit/test_window_ops.py`
- [x] T009 [US3] Implement `Window.set_topmost` in `src/nge2/window/__init__.py`

## Phase 6: User Story 4 — Move outer frame (P2)

**Goal**: Move outer top-left to screen `(x,y)`; no resize; not client-relative  
**Independent test**: Fake records position; size preserved by helper contract

- [x] T010 [P] [US4] Unit tests for move target and screen coords in `tests/unit/test_window_ops.py`
- [x] T011 [US4] Implement `Window.move` in `src/nge2/window/__init__.py`

## Phase 7: Polish

- [x] T012 Add `examples/window_smoke.py` and document in `examples/README.md`
- [x] T013 Run `uv run pytest tests/unit/test_window_ops.py tests/unit/test_window_coords.py -q` green; mark all tasks `[x]`

## Dependencies

- US1 before polish smoke that relies on find
- US2–US4 independent after T002–T003
- T004 before T005 recommended (tests first)

## MVP

T001–T005 (find) delivers discovery; then activate/topmost/move.

## Parallel opportunities

- T003 || after T002
- T004 || T006 || T008 || T010 once helpers exist
- T005/T007/T009/T011 sequential on same file after their tests
