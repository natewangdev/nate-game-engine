# Implementation Plan: Vision wait/poll

**Branch**: `007-vision-wait` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

Chinese companion: [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Add shared wall-clock poll helper; `ocr.find_text` (substring, multi/single); extend `find_image` and `yolo.detect` with `timeout_ms` / `interval_ms`. No new dependencies.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Existing RapidOCR / OpenCV / ORT; stdlib `time`  
**Testing**: pytest + FakeCapture / FakeOcr / FakeYolo; monkeypatch sleep/monotonic  
**Target Platform**: Windows  
**Project Type**: Library incremental  
**Constraints**: Wall-clock ms; `timeout_ms < interval_ms` (when timeout>0) → `FindError`; YOLO timeout → `[]`  

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I–III | PASS | Library API; faked poll tests |
| IV | PASS | No new deps |
| V–VII | PASS | Additive; bilingual |

## Project Structure

```text
src/nge2/_vision.py          # validate_wait, poll_until
src/nge2/ocr/__init__.py     # find_text
src/nge2/find/__init__.py    # find_image timeout params
src/nge2/yolo/__init__.py    # detect timeout params
tests/fakes.py               # FakeOcr.find_text; FakeYolo poll-aware detect
tests/unit/test_vision_wait.py
examples/ (optional smoke notes in README)
```

## Complexity Tracking

None.
