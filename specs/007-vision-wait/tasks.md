# Tasks: Vision wait/poll

Chinese companion: [`tasks.zh-CN.md`](./tasks.zh-CN.md).

- [x] T001 Add `validate_wait` + `poll_until` (+ monkeypatch seams) in `src/nge2/_vision.py`
- [x] T002 [P] Unit tests for wait validation / poll early-exit in `tests/unit/test_vision_wait.py`
- [x] T003 [US1] Implement `Ocr.find_text` in `src/nge2/ocr/__init__.py`; update `tests/fakes.py` FakeOcr
- [x] T004 [US2] Add `timeout_ms`/`interval_ms` to `Find.find_image` in `src/nge2/find/__init__.py`
- [x] T005 [US3] Add `timeout_ms`/`interval_ms` to `Yolo.detect` in `src/nge2/yolo/__init__.py`; update FakeYolo
- [x] T006 [P] Story tests (find_text / find_image poll / detect poll) in `tests/unit/test_vision_wait.py`
- [x] T007 Document briefly in `examples/README.md`; `uv run pytest -q` green; mark tasks `[x]`
