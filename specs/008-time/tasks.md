# Tasks: Time module

Chinese companion: [`tasks.zh-CN.md`](./tasks.zh-CN.md).

- [x] T001 Create `src/nge2/time/__init__.py` with shared `sleep`/`delay`, `Time` static methods, `_sleep`/`_randint` seams, integer validation → `ValueError`
- [x] T002 Wire `self.time = Time()` in `src/nge2/_engine.py` (no open/close gate); add `time` to constitution domain lists (EN + zh-CN)
- [x] T003 [P] Unit tests in `tests/unit/test_time.py` (fixed, random, alias, three surfaces, illegal args, closed engine)
- [x] T004 [P] Add `examples/time_smoke.py` + README entry; `uv run pytest tests/unit/test_time.py -q` green; mark tasks `[x]`
