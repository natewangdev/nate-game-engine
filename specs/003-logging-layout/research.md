# Research: Logging Layout

**Feature**: `003-logging-layout` | **Date**: 2026-09-27

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. Per-instance file handlers on shared root

- **Decision**: Keep logger root `nge`. On each `NGE2` construct, attach a dedicated `FileHandler` to that day’s `nge-NNN.log` and an `ErrorScreenshotHandler` bound to that instance (weakref). On `close()`, remove those handlers.
- **Rationale**: Multi-instance needs separate files; shared root still allows `get_logger`.
- **Alternatives**: Per-instance logger trees — breaks existing `nge.*` usage.

## 2. Index allocation

- **Decision**: Glob `nge-*.log` in day dir; parse trailing integer; next = max+1; format with `f"nge-{n:03d}.log"` when n < 1000 else `f"nge-{n}.log"`.
- **Rationale**: Spec Q1.

## 3. ERROR screenshot rendering

- **Decision**: Use Pillow: BGR→RGB, `ImageDraw` text with stroke (black outline, white fill), fonts from YaHei/SimHei/msyh.ttc fallbacks. Save JPEG quality ~90.
- **Rationale**: OpenCV `putText` cannot render Chinese reliably.
- **Alternatives**: Win32 DrawText — more code; skip Chinese — rejected.

## 4. Recursion guard

- **Decision**: Screenshot failures logged at WARNING (not ERROR) with a thread-local/reentrancy flag so ERROR hook does not re-enter.
- **Rationale**: Soft-fail without infinite screenshot loops.

## 5. Removing enable_file_logging

- **Decision**: Delete parameter; tests pass `log_dir=tmp_path / "logs"`.
- **Rationale**: Spec FR-011 / Q7.
