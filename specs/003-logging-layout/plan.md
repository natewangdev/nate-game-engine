# Implementation Plan: Dated File Logging and Error Screenshots

**Branch**: `003-logging-layout` | **Date**: 2026-09-27 | **Spec**: [spec.md](./spec.md)

Chinese companion: [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Replace flat `cwd/nge.log` + `enable_file_logging` with `NGE2(log_dir=...)` (default `{cwd}/logs`), per-day `nge-NNN.log` files, nameless console/file format, and an ERROR-only screenshot hook (window client or first display → annotated JPEG under `screenshot/`). Add **Pillow** for CJK overlay on BGR frames.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Existing capture stack + **Pillow** (JPEG save + TrueType CJK text)  
**Storage**: Local filesystem under `log_dir`  
**Testing**: pytest; temp dirs; FakeCapture; no real display required for CI  
**Target Platform**: Windows (fonts under `C:\Windows\Fonts`)  
**Project Type**: Library incremental feature  
**Constraints**: Soft-fail screenshots; no midnight rollover; exact ERROR level only  
**Scale/Scope**: `nge2.log` + `_engine` wiring; tests update

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I. Library-first | PASS | `log_dir` on `NGE2` |
| II. Side-effect isolation | PASS | Screenshot via capture facade; fakes in CI |
| III. Tests | PASS | Layout + ERROR hook tests |
| IV. Full install / YAGNI | PASS | Pillow justified for CJK overlay |
| V. SemVer | PASS | Additive `log_dir`; remove `enable_file_logging` (pre-1.0) |
| VI–VII. Bilingual | PASS | Paired artifacts |

**Post-design**: PASS.

## Project Structure

```text
specs/003-logging-layout/   # this feature docs
src/nge2/log/__init__.py    # layout, format, handlers
src/nge2/log/_screenshot.py # overlay + save (optional split)
src/nge2/_engine.py         # log_dir; remove enable_file_logging; wire hook
tests/unit/test_logging_layout.py
```

**New dependency**: `pillow` — draw Chinese text with outline on screenshots.

## Complexity Tracking

None.
