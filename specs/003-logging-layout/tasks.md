# Tasks: Dated File Logging and Error Screenshots

**Input**: `/specs/003-logging-layout/`

Chinese companion: [`tasks.zh-CN.md`](./tasks.zh-CN.md).

**Tests**: Included (FR-012).

---

## Phase 1: Setup

- [x] T001 Add `pillow` to `pyproject.toml` / `uv.lock` runtime dependencies

## Phase 2: Foundational

- [x] T002 Rewrite format (no `%(name)s`) and day-layout helpers in `src/nge2/log/__init__.py`
- [x] T003 Implement next `nge-NNN` / screenshot index scanners in `src/nge2/log/__init__.py`

## Phase 3: US1 — Log directory & files

- [x] T004 [P] [US1] Unit tests for default/explicit `log_dir`, index increment, format without module name in `tests/unit/test_logging_layout.py`
- [x] T005 [US1] Wire `log_dir` into `NGE2` and remove `enable_file_logging` in `src/nge2/_engine.py`; attach per-instance FileHandler; detach on close
- [x] T006 [US1] Update existing tests that passed `enable_file_logging=False` to use `log_dir=tmp_path / "logs"`

## Phase 4: US2 — ERROR screenshots

- [x] T007 [P] [US2] Tests for ERROR → jpg under screenshot/; INFO no shot; soft-fail in `tests/unit/test_logging_layout.py`
- [x] T008 [US2] Implement overlay+JPEG save and ErrorScreenshotHandler in `src/nge2/log/` (Pillow + font fallbacks)
- [x] T009 [US2] Bind handler to engine capture/hwnd in `src/nge2/_engine.py`

## Phase 5: Polish

- [x] T010 Update README / examples notes if they mention `nge.log` or `enable_file_logging`
- [x] T011 Run `uv run pytest -q` until green; mark tasks complete

---

## Dependencies

T001 → T002 → T003 → US1 (T004–T006) → US2 (T007–T009) → Polish
