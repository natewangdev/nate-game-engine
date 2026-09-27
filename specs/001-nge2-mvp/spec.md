# Feature Specification: nge2 MVP Core Engine

**Feature Branch**: `001-nge2-mvp`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "Nate Game Engine MVP — package `nge2` with NGE2 engine instance, capture, HID control, geom, window, log; find stub; OCR/YOLO deferred"

## Clarifications

### Session 2026-09-26

- Q: After `capture.release()` has torn down the backend, what must a later `grab()` on the same engine do? → A: Subsequent `grab()` auto-recreates the same capture backend and succeeds (Option A).
- Q: Must `NGE2` expose an explicit shutdown so HID serial and capture are released when the script is done? → A: Must provide `close()` and context-manager (`with`) support; exit releases this instance's HID and capture (Option A).
- Q: If the requested capture backend cannot be created at engine construction, what must happen? → A: Construction fails immediately with a clear error that the chosen backend is unavailable; no automatic fallback to another backend (Option A).
- Q: For this MVP, should the `ocr` and `yolo` modules exist as importable stubs or be omitted? → A: MVP ships importable `ocr`/`yolo` stubs; using their capability APIs raises `NotImplementedError` (same pattern as `find`) (Option A).
- Q: If one `NGE2` instance already holds the ESP32-S3 serial port, what must happen when a second instance constructs with `control_mode=2`? → A: Second instance construction fails immediately with a clear actionable error that the port/device is busy (Option A).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Construct an engine and capture the screen (Priority: P1)

A script author creates an `nge2.NGE2` engine with a required resource directory and capture backend choice, then grabs a full-screen or regional frame as a BGR image array for later scripting steps.

**Why this priority**: Capture is the sensing foundation; without it, downstream vision features cannot work.

**Independent Test**: Construct an engine with a valid resource directory and a mockable/real capture backend; call grab full-screen and grab with a region; release the backend; verify frames are BGR arrays of expected shape.

**Acceptance Scenarios**:

1. **Given** a writable resource directory path and an available capture backend, **When** the author constructs `NGE2` with that backend, **Then** construction succeeds and `engine.capture` is available on that instance only.
2. **Given** the requested capture backend cannot be created, **When** construction is attempted, **Then** construction fails immediately with a clear error and does not fall back to another backend.
3. **Given** a constructed engine, **When** the author calls grab without a region, **Then** a BGR frame of the first display is returned.
4. **Given** a constructed engine, **When** the author calls grab with a screen-physical-pixel region, **Then** a BGR crop of that region is returned.
5. **Given** a constructed engine, **When** the author calls release on capture, **Then** the capture backend is torn down; a later `grab()` on the same engine MUST recreate the same backend and succeed.

---

### User Story 2 - Control mouse and keyboard via hardware HID (Priority: P1)

A script author connects to an ESP32-S3 HID device (auto-discovered serial port) through the engine and performs moves, clicks, and key actions. With humanize enabled, moves follow a human-like path; with humanize disabled, moves are instantaneous.

**Why this priority**: HID input delivery is the core actuation value of this MVP.

**Independent Test**: With a real device or a mocked serial transport, exercise move, left/right click with hold, left/right button down/up, move-and-click, key down/up/click (including modifiers); verify failure when no device is found at construction.

**Acceptance Scenarios**:

1. **Given** an ESP32-S3 is connected and discoverable, **When** the author constructs `NGE2` with `control_mode=2` (default), **Then** construction succeeds after auto-discovering the serial port.
2. **Given** no matching HID serial device, **When** construction with `control_mode=2` is attempted, **Then** construction fails with a clear error.
3. **Given** one engine already holding the HID serial port, **When** a second `NGE2` with `control_mode=2` is constructed, **Then** construction fails immediately with a clear actionable error that the port/device is busy.
4. **Given** an engine with `humanize=True`, **When** the author moves to a target with duration and spread, **Then** the pointer follows a generated human-like path and the final point lies within the spread disk when spread > 0.
5. **Given** an engine with `humanize=False`, **When** the author moves with duration/spread arguments, **Then** the pointer jumps instantly and duration/spread have no effect.
6. **Given** a constructed engine, **When** the author left-clicks or right-clicks at the current position with an optional hold, **Then** a click is issued at the current pointer position for the specified or default hold duration.
7. **Given** a constructed engine, **When** the author calls left or right button down / up at the current position, **Then** the corresponding mouse button is pressed or released without an automatic paired release (caller owns pairing); these are distinct from full clicks.
8. **Given** a constructed engine, **When** the author calls move-and-click to a target, **Then** the pointer moves (per humanize rules) then clicks.
9. **Given** a constructed engine, **When** the author uses key_click / key_down / key_up with friendly key names and modifiers, **Then** the device receives the corresponding HID actions; key_click performs down→up with an inter-key interval.

---

### User Story 3 - Bind a window and use client-relative coordinates (Priority: P2)

A script author passes a window handle at construction. Subsequent move and related coordinates are interpreted relative to the window client area (physical pixels). The author can query the bound handle, title, and client visual region via the window module.

**Why this priority**: Window-relative scripting is a common game-bot need and depends on DPI-aware physical pixels.

**Independent Test**: Construct with a known hwnd (or fake window metrics in unit tests for conversion); verify relative-to-screen conversion and window query APIs.

**Acceptance Scenarios**:

1. **Given** a valid hwnd, **When** the engine is constructed, **Then** the process is made DPI-aware and coordinates use physical pixels.
2. **Given** a bound hwnd, **When** the author moves to `(x, y)`, **Then** the target is treated as client-area-relative and converted to screen space via client rect + client-to-screen.
3. **Given** a bound hwnd, **When** the author queries window APIs, **Then** they receive the hwnd, title, and client-area geometry (client and/or screen rectangles as documented).
4. **Given** no hwnd, **When** the author moves to `(x, y)`, **Then** coordinates are absolute screen physical pixels.

---

### User Story 4 - Observe logs and refuse unimplemented control modes (Priority: P3)

A script author relies on package logging (console + file, level via `NGE_LOG_LEVEL`) and receives immediate failure when requesting foreground/background control modes that are reserved but not implemented in this release.

**Why this priority**: Operability and honest API boundaries prevent silent misuse.

**Independent Test**: Construct with mode 0 or 1 and expect failure; enable file logging and verify messages under logger root `nge`.

**Acceptance Scenarios**:

1. **Given** any resource directory, **When** construction uses `control_mode` 0 or 1, **Then** construction fails immediately stating the mode is not implemented (API reserved).
2. **Given** a constructed engine, **When** logging occurs, **Then** messages appear on the console and in a log file under logger hierarchy rooted at `nge`, with level controlled by `NGE_LOG_LEVEL`.
3. **Given** a constructed engine used as a context manager or closed via `close()`, **When** the block exits or `close()` returns, **Then** this instance's HID serial connection and capture backend are released.

---

### Edge Cases

- Multiple `NGE2` instances in one process each own a separate capture backend; they do not share capture state.
- If one instance already holds the HID serial port, a second `NGE2` construction with `control_mode=2` MUST fail immediately with a clear actionable error (port/device busy).
- Capture always uses the **first display** even if the bound window is on a secondary monitor (accepted limitation; relative client coords may not align with the captured frame).
- Invalid or destroyed hwnd: construction or later coordinate conversion fails with a clear error.
- Requested capture backend unavailable at construction: fail immediately; no silent fallback to another backend.
- Unknown key names for keyboard APIs fail clearly without sending partial HID traffic when resolution fails before send.
- Calling `find` module APIs raises `NotImplementedError` (stub only).
- Calling `ocr` or `yolo` capability APIs raises `NotImplementedError` (importable stubs in MVP; full behavior deferred).
- Releasing capture then grabbing again: `grab()` MUST re-initialize the same backend and succeed.
- After `close()` (or exiting a `with` block), further use of that engine's capture/control MUST fail clearly; a new `NGE2` instance is required.
- If a mouse button is left down when `close()` runs, STOP on the device MUST release held buttons; callers SHOULD still pair down/up in normal scripts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The distribution display name is "Nate Game Engine"; PyPI name is `nate-game-engine`; import package name MUST be `nge2`.
- **FR-002**: The primary entry MUST be an instance API: `engine = nge2.NGE2(...)`; module access MUST be `engine.<module>.…` (e.g. `engine.capture.grab()`). Multiple independent instances MUST be supported. `NGE2` MUST provide `close()` and MUST support use as a context manager (`with`); closing MUST release that instance's HID connection (mode 2) and capture backend.
- **FR-003**: `NGE2` construction MUST accept: `capture` (`"dxcam"` | `"mss"`, default `"dxcam"`), `hwnd` (`None` default), `humanize` (`bool`, default `True`), `control_mode` (`int`, default `2`), `resource_dir` (required; relative paths resolved against process cwd; no mandated subdirectory layout). If the requested capture backend cannot be created, construction MUST fail immediately with a clear error and MUST NOT automatically fall back to another backend.
- **FR-004**: Construction MUST declare the process DPI-aware; all coordinates in this feature are physical pixels.
- **FR-005**: When `control_mode` is `0` or `1`, construction MUST fail immediately as not implemented (APIs reserved for later). When `control_mode` is `2`, construction MUST auto-discover an ESP32-S3 serial port and MUST fail construction if none is found. If another `NGE2` instance in the same process already holds that serial port, a subsequent construction with `control_mode=2` MUST fail immediately with a clear actionable error (port/device busy).
- **FR-006**: Each `NGE2` instance MUST own its own `capture` lifecycle (not a process-global singleton).
- **FR-007**: `capture` MUST support grab full first-display frame and grab by optional region; return type MUST be a BGR image array. Region coordinates MUST be screen physical pixels. Capture MUST provide a release operation for the backend. After release, a subsequent `grab()` on the same engine MUST recreate the same backend and succeed.
- **FR-008**: `control` in this feature MUST implement hardware HID mode only (ESP32-S3), with mouse move, left/right click at current position with hold (default when omitted), left/right mouse button down and up at current position (no automatic pair; distinct from full click), move-and-click, key_click (down→up with interval, modifiers supported), key_down, and key_up. Friendly key names MUST map to HID Usage IDs equivalently to the established keymap contract from the prior nge toolkit. Button down/up MUST use the HID `BTN` line command; full clicks MAY continue to use `CLK`.
- **FR-009**: When `humanize` is `True`, moves MUST use internally generated human-like paths (`geom` is internal-only). The default `spread` for `move` and move-related APIs that accept `spread` (e.g. `drag`, `move_and_click`) MUST be `10.0` (pixels). `double_click` is excluded and MUST NOT apply landing scatter. When `humanize` is `False`, moves MUST be instantaneous and MUST ignore duration and spread.
- **FR-010**: With `hwnd` set, move/click target coordinates MUST be client-relative; conversion MUST use Win32 client rect + client-to-screen. Without `hwnd`, coordinates MUST be screen absolute.
- **FR-011**: `window` MUST expose the bound hwnd (if any), window title, and client visual region (Win32 client area).
- **FR-012**: `log` MUST support console and file logging under root name `nge`, with level from environment variable `NGE_LOG_LEVEL`. *(File path layout, `log_dir` constructor parameter, ERROR screenshots, and log line format without module names are superseded by feature `003-logging-layout` once implemented.)*
- **FR-013**: `geom` MUST NOT be part of the stable public scripting surface; it exists to serve `control` humanize paths.
- **FR-014**: `find` MUST exist as a public stub that raises `NotImplementedError` on use.
- **FR-015**: OCR and YOLO **recognition/detection behavior** is out of scope for this MVP (deferred). The installed package MUST still expose importable `ocr` and `yolo` modules as stubs; invoking their capability APIs MUST raise `NotImplementedError`. Stub presence alone is not MVP functional acceptance beyond importability and the explicit error.
- **FR-016**: Default install MUST be full (all runtime deps for supported MVP modules in the base set), per constitution v1.2.0.
- **FR-017**: Automated CI MUST cover pure logic with mocked serial and mocked capture; real ESP32-S3 and real screen checks are manual/optional.

### Key Entities

- **Engine (`NGE2`)**: Per-instance configuration and facade over modules; owns capture and HID connection lifecycle for mode 2; supports `close()` and context-manager shutdown.
- **Capture session**: Backend (`dxcam` or `mss`) bound to one engine; produces BGR frames.
- **HID connection**: Serial link to ESP32-S3 firmware speaking the established line protocol.
- **Window binding**: Optional hwnd plus derived client geometry for coordinate mapping.
- **Humanize path**: Ordered waypoints with delays produced for a move when humanize is enabled.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A script author can construct an engine with a resource directory and obtain a BGR full-screen frame in under 5 seconds on a typical Windows desktop (excluding first-time dependency install).
- **SC-002**: With a connected ESP32-S3, construction with default control mode succeeds; without a device, construction fails with an actionable error in 100% of attempts.
- **SC-003**: Authors can complete the sequence move → left_click → key_click (and, when needed, left_down / left_up) for a documented sample script without changing package internals.
- **SC-004**: With a bound hwnd, client-relative moves land within the intended client region under 100%/125%/150% display scaling (physical-pixel correctness).
- **SC-005**: Constructing with control_mode 0 or 1 fails before any HID or capture side effects beyond DPI declaration.
- **SC-006**: CI pure-logic suite (mocked I/O) passes without a physical device or interactive desktop session.

## Assumptions

- Hold default when omitted for clicks matches prior toolkit behavior: random human-like hold roughly 45–110 ms unless an explicit hold (seconds) is passed.
- Mouse button down/up APIs do not move the pointer; they act at the current pointer position only (same as left_click / right_click).
- Key-click inter-press interval uses a short human-like delay consistent with the prior toolkit (on the order of tens of milliseconds).
- Default log file path is under the process cwd (e.g. `nge.log`) unless otherwise set via a documented logger helper. *(Superseded by `003-logging-layout`: default `{cwd}/logs/{date}/nge-NNN.log`.)*
- `grab(region=...)` always uses **screen** physical pixels, even when an hwnd is bound.
- Capture on secondary-monitor windows remaining misaligned with first-display grabs is an accepted product limitation for this feature.
- Foreground/background control modes remain API-reserved; only construction-time rejection is required in MVP (no partial pywinauto implementation).
- Prior reference implementations under `nate-gaming-engine` inform behavioral contracts (HID protocol, keymap, humanize) but are not vendored as a dependency.
- Package layout rebuilds from `nate_game_engine` stubs to `nge2` with the eight named modules (`capture`, `control`, `ocr`, `yolo`, `find`, `log`, `geom`, `window`) as part of implementing this feature; `ocr`/`yolo`/`find` are stubs in MVP.

## Out of Scope

- OCR (RapidOCR) and YOLO detection **behavior** (specified later); MVP still ships importable stubs.
- Find-image / find-color implementation (stub only).
- Foreground and background keyboard/mouse backends (pywinauto).
- Multi-monitor capture selection beyond “first display”.
- Non-Windows platforms.
