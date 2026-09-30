# Research: Vision wait/poll

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. Shared poll helper

- **Decision**: `validate_wait` + `poll_until` in `_vision.py`; monkeypatchable `_sleep` / `_monotonic`.
- **Rationale**: One wall-clock semantics for OCR/find/YOLO; CI without real time.
- **Alternatives**: Per-module copy — rejected (drift).

## 2. find_text

- **Decision**: Filter `recognize` results with casefold substring; `multi` shapes return; default `interval_ms=1000`.
- **Rationale**: Locked clarify B/A; reuse grab/OCR path.
- **Alternatives**: Separate RapidOCR call — rejected.

## 3. find_image / detect

- **Decision**: Wrap one-shot attempt in `poll_until`; defaults 500ms interval.
- **Rationale**: Spec US2/US3; minimal surface change.
- **Alternatives**: New `wait_find_image` — rejected (prefer params).

## 4. YOLO empty vs None

- **Decision**: Timeout returns `[]` (clarify C).
- **Rationale**: Preserve list-only type for callers.
