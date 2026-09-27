# Implementation Plan: Find Image and Find Color

**Branch**: `004-find-vision` | **Date**: 2026-09-27 | **Spec**: [spec.md](./spec.md)

Chinese companion: [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Replace find stubs with an engine-bound `Find` facade: `find_image` / `find_images` (OpenCV `TM_CCOEFF_NORMED`, threshold 0.7, NMS) and `find_color` (RGB/#hex + tolerance). Fresh `capture.grab` each call; coords align with `move`. Add **opencv-python-headless** to base deps.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: numpy, opencv-python-headless (matchTemplate / imdecode)  
**Testing**: pytest + FakeCapture synthetic frames  
**Target Platform**: Windows  
**Project Type**: Library incremental  
**Constraints**: First-display capture; hwnd client-relative returns  

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I–III | PASS | Library API; FakeCapture tests |
| IV | PASS | opencv-python-headless justified for vision |
| V–VII | PASS | Additive; bilingual docs |

## Project Structure

```text
src/nge2/find/__init__.py   # Find facade, Match, ColorMatch
src/nge2/find/_match.py     # pure cv2 helpers (optional)
src/nge2/window/__init__.py # screen_to_client
src/nge2/_engine.py         # wire Find instance
src/nge2/_errors.py         # FindError
tests/unit/test_find.py
examples/find_smoke.py
```

## Complexity Tracking

None.
