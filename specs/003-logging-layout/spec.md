# Feature Specification: Dated File Logging and Error Screenshots

**Feature Branch**: `003-logging-layout`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "NGE2 log_dir init param (default cwd/logs); daily folders with zero-padded per-start nge-NNN.log; on logger.error take window/fullscreen JPG with Chinese caption; console and file formats omit logger module name; remove enable_file_logging."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

**Supersedes (partial)**: `001-nge2-mvp` FR-012 / Assumptions about default `nge.log` under cwd and optional `enable_file_logging`. After this feature, file logging layout and the `log_dir` constructor parameter defined here are authoritative.

## Clarifications (locked)

| Topic | Decision |
|-------|----------|
| Daily index | Scan day’s `nge-*.log`, next index = max+1; zero-padded to **3** digits (`nge-001.log`) |
| Midnight / long run | **A**: Entire process uses the calendar day folder chosen at engine construct (local timezone) |
| Multiple `NGE2` | **A**: Each instance opens its own log file (each increments index) |
| Screenshot trigger | **Only** `logging.ERROR` / `logger.error(...)` (not warning, not critical-only unless logged as ERROR, no sys.excepthook) |
| Screenshot format | JPEG (`.jpg`) |
| Screenshot name | `{log_dir}/{YYYY-MM-DD}/screenshot/{HHMMSS}-{xxx}.jpg` where `{xxx}` is a 3-digit zero-padded per-day counter |
| Overlay | White text + black outline; Chinese must render clearly |
| Screenshot failure | Log a failure message only; MUST NOT raise to caller / block business |
| Format | Console and file: **no** logger name (no `nge.capture`) |
| `enable_file_logging` | **Removed**; file logging always enabled when `NGE2` constructs successfully |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure log directory and daily files (Priority: P1)

A script author passes `log_dir` when constructing `NGE2`, or omits it and gets `{cwd}/logs`. On construct, the engine creates `{log_dir}/{YYYY-MM-DD}/` if needed and opens a new `nge-{NNN}.log` for this instance start. Console and file lines omit module names.

**Why this priority**: Core observability path for all scripts.

**Independent Test**: Construct with temp `log_dir`; assert directory creation, `nge-001.log` then second instance `nge-002.log`; assert line format has no `nge.` module segment; assert default uses cwd `logs`.

**Acceptance Scenarios**:

1. **Given** no `log_dir`, **When** `NGE2` is constructed, **Then** logs go under `{process cwd}/logs/{YYYY-MM-DD}/nge-NNN.log` (folder created if missing).
2. **Given** an explicit `log_dir`, **When** constructed, **Then** logs go under `{log_dir}/{YYYY-MM-DD}/nge-NNN.log`.
3. **Given** the day’s folder already has `nge-001.log` and `nge-002.log`, **When** a new engine starts that day, **Then** it creates `nge-003.log`.
4. **Given** a long-running engine that crosses midnight, **When** logging continues, **Then** it keeps writing to the start-day file/folder (no automatic day switch).
5. **Given** two engines in one process, **When** both construct, **Then** each has its own incremented log file.
6. **Given** logging to console and file, **When** a message is emitted, **Then** neither stream includes the logger hierarchical name (e.g. no `nge.capture`).

---

### User Story 2 - Capture annotated screenshot on ERROR (Priority: P1)

When code logs at ERROR via the package loggers, the engine also grabs a screenshot (bound window client area if `hwnd` was set at construct; otherwise full first display), draws local time and the error message at the top-left in clear Chinese-capable white text with black outline, and saves a JPEG under that day’s `screenshot` subfolder. Failures capturing/saving only produce a log line and do not break the caller.

**Why this priority**: Critical for debugging game scripts without attaching a debugger.

**Independent Test**: Fake/mock capture; call `logger.error("…")`; assert JPEG path pattern and that business API is not failed when capture raises.

**Acceptance Scenarios**:

1. **Given** an engine with `hwnd` set, **When** `logger.error("失败原因")` is called, **Then** a JPEG is written under `{log_dir}/{date}/screenshot/{HHMMSS}-{xxx}.jpg` showing the window client region with time + message overlaid top-left.
2. **Given** an engine without `hwnd`, **When** ERROR is logged, **Then** the screenshot is the full first-display frame with the same overlay rules.
3. **Given** capture or save fails, **When** ERROR is logged, **Then** an additional log line reports the screenshot failure and the original ERROR logging still completes without raising to the caller.
4. **Given** INFO/WARNING logs, **When** they are emitted, **Then** no screenshot is taken.

---

### Edge Cases

- `log_dir` is a relative path: resolve against process cwd at construct.
- Day string uses local timezone `YYYY-MM-DD`.
- Index padding: 3 digits (`nge-001` … `nge-999`); if more than 999 files exist in one day, continue with wider width without failing (e.g. `nge-1000.log`).
- Screenshot `{xxx}`: zero-padded 3-digit counter of ERROR screenshots already written that day in that folder (max+1), independent of log file index.
- Very long error messages: truncate overlay text to a documented max length so the image remains readable (e.g. first 200 characters + ellipsis).
- Engine closed / capture released: ERROR screenshot attempt fails soft (log only).
- Constructor parameter `enable_file_logging` MUST NOT be accepted (removed API).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `NGE2` MUST accept `log_dir: str | Path | None = None`. When `None`, MUST use `{cwd}/logs`. MUST create the directory (and day subdirectory) if missing.
- **FR-002**: On each successful `NGE2` construct, MUST open a **new** log file at `{log_dir}/{YYYY-MM-DD}/nge-{NNN}.log` where `{NNN}` is zero-padded to 3 digits and equals one more than the maximum existing index among `nge-*.log` in that day folder (or `001` if none).
- **FR-003**: The calendar day folder MUST be fixed at construct time (local date); midnight MUST NOT switch the active file for that instance.
- **FR-004**: Each `NGE2` instance MUST use its own log file (multi-instance → multiple files / indices).
- **FR-005**: File and console log records MUST NOT include the logger name field (no `nge.capture` / `%(name)s`).
- **FR-006**: Log level remains controlled by `NGE_LOG_LEVEL` (default INFO) unless otherwise documented.
- **FR-007**: When a log record at level ERROR is handled for the engine’s logging configuration, MUST attempt a screenshot: with `hwnd` → window client visual region; without `hwnd` → full first-display frame (same capture constraints as MVP first display).
- **FR-008**: Screenshot MUST be JPEG (`.jpg`) saved under `{log_dir}/{YYYY-MM-DD}/screenshot/` (create if missing) named `{HHMMSS}-{xxx}.jpg` where `{HHMMSS}` is local time of the error and `{xxx}` is a 3-digit zero-padded per-day screenshot sequence (max+1).
- **FR-009**: Overlay MUST place local timestamp and the error message at the top-left; text MUST be white with black outline; Chinese glyphs MUST render clearly (engine MUST pick a font available on Windows that supports the message characters, with a documented fallback chain).
- **FR-010**: Screenshot capture/draw/save failures MUST be logged and MUST NOT propagate an exception to the code that called `logger.error`.
- **FR-011**: `enable_file_logging` MUST be removed from `NGE2` construction; file logging is always on for constructed engines.
- **FR-012**: Automated tests MUST cover directory/index selection and ERROR screenshot side effects with fakes/mocks (no real desktop required for CI).

### Key Entities

- **LogLayout**: Root `log_dir`, day folder, instance log file path, screenshot folder.
- **LogFileIndex**: Zero-padded sequence among `nge-*.log` for a day.
- **ErrorScreenshot**: JPEG path, overlay payload (time + message), source region (window vs full screen).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authors can omit `log_dir` and find logs under `logs/{date}/nge-001.log` after first construct from cwd.
- **SC-002**: A second construct the same day produces `nge-002.log` (or next free index) without overwriting.
- **SC-003**: An ERROR log produces a JPEG under that day’s `screenshot/` with readable Chinese overlay in ≥ documented smoke check.
- **SC-004**: Log lines in console and file do not contain `nge.` module name prefixes.
- **SC-005**: CI tests for layout and ERROR screenshot hooks pass without a physical display when fakes are injected.

## Assumptions

- Local timezone for date/time formatting.
- Overlay truncation length default 200 characters unless plan chooses another constant.
- Font fallback starts from common Windows CJK fonts (e.g. Microsoft YaHei, SimHei, Segoe UI) then a safe default.
- MVP capture “first display only” still applies to fullscreen ERROR shots.
- This feature may register a logging handler/filter tied to the engine instance so ERROR hooks can access that instance’s `hwnd` and capture.

## Out of Scope

- Log rotation by size inside a single run
- Automatic day rollover at midnight for a running instance
- Screenshots for WARNING/CRITICAL unless logged as ERROR
- Global `sys.excepthook` integration
- Remote log shipping
- Changing logger root name away from `nge`
