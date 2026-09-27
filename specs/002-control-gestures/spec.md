# Feature Specification: Control Gestures (Drag, Scroll, Double-Click, Hotkey Alias)

**Feature Branch**: `002-control-gestures`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "Add control drag (press-move-release, default left), mouse wheel scroll by direction and notches (legacy nge delta ±1, clamp ±127), left-button double-click only, and formalize chord APIs as key_click(*keys) plus hotkey(*keys) alias (no ctrl+c string form)."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Drag pointer while holding a mouse button (Priority: P1)

A script author needs to drag from one point to another (for example UI sliders or map panning). They call a single drag operation that moves to the start, presses a mouse button (default left), moves to the end following the engine's existing move/humanize rules, then releases the button.

**Why this priority**: Highest new actuation value; composes existing move and button press/release into a reliable gesture.

**Independent Test**: With a mocked HID transport (or real device), invoke drag between two points for left and right buttons; verify press occurs after reaching the start, moves occur while held, and release occurs at the end.

**Acceptance Scenarios**:

1. **Given** a constructed engine, **When** the author drags from `(x1,y1)` to `(x2,y2)` with default button, **Then** the pointer reaches the start, the left button is pressed, the pointer moves to the end per humanize rules, and the left button is released.
2. **Given** a constructed engine, **When** the author drags with the right button selected, **Then** the same press-move-release sequence uses the right button.
3. **Given** an engine with a bound window handle, **When** the author drags using client-relative coordinates, **Then** start and end points are interpreted like other move targets (client-relative vs screen absolute).
4. **Given** `humanize=False`, **When** the author drags with duration/spread arguments, **Then** start and end jumps are instantaneous and duration/spread do not affect path generation (same rules as move).

---

### User Story 2 - Scroll the mouse wheel by direction and notches (Priority: P1)

A script author scrolls content up or down by a number of discrete wheel notches without moving the pointer. Behavior matches the prior nge toolkit: positive delta scrolls up, negative scrolls down, one notch equals one unit of delta, and the sent delta is clamped to a safe device range.

**Why this priority**: Common game/UI automation need; previously missing from the public control surface.

**Independent Test**: Mocked transport records wheel commands for up/down and multi-notch values; invalid notch counts fail clearly before send.

**Acceptance Scenarios**:

1. **Given** a constructed engine, **When** the author scrolls up by N notches (N ≥ 1), **Then** the device receives a single upward wheel action whose magnitude is N (subject to clamp).
2. **Given** a constructed engine, **When** the author scrolls down by N notches, **Then** the device receives a single downward wheel action whose magnitude is N (subject to clamp).
3. **Given** a constructed engine, **When** the author requests a notch count that is not a positive integer, **Then** the call fails with a clear error and no wheel command is sent.
4. **Given** a constructed engine, **When** the author scrolls, **Then** the pointer position is not moved by the scroll API itself.

---

### User Story 3 - Double-click with the left mouse button (Priority: P2)

A script author double-clicks the left button at the current position or after moving to a target. Two complete left clicks occur with a short interval between them.

**Why this priority**: Frequent UI pattern; scoped to left button only for this feature.

**Independent Test**: Mocked transport shows two left-click actions with an interval; optional pre-move then double-click.

**Acceptance Scenarios**:

1. **Given** a constructed engine, **When** the author double-clicks without coordinates, **Then** two left clicks occur at the current pointer position with a short interval between them.
2. **Given** a constructed engine, **When** the author double-clicks with target coordinates, **Then** the pointer moves to the target (per humanize rules) and then two left clicks occur.
3. **Given** a constructed engine, **When** the author supplies an explicit hold and/or interval, **Then** those values are used for the clicks and the gap between clicks.
4. **Given** a constructed engine, **When** the author double-clicks at a target (or current position), **Then** both clicks land on the same point with no random target scatter.

---

### User Story 4 - Formalize keyboard chords via key_click and hotkey alias (Priority: P3)

A script author triggers modifier chords such as Ctrl+C using the existing multi-argument key click style. This feature documents and aliases that capability as the official chord API (no `"ctrl+c"` string parsing). A `hotkey` alias calls the same behavior as `key_click` for discoverability.

**Why this priority**: Capability largely exists; this story locks the contract, docs, and alias so authors do not invent a third API.

**Independent Test**: Mocked transport exercises `key_click('ctrl','c')` and `hotkey('ctrl','shift','esc')` (or equivalent); unknown keys fail before send.

**Acceptance Scenarios**:

1. **Given** a constructed engine, **When** the author calls `key_click` with one or more modifier names followed by a main key, **Then** the device receives the corresponding chord (modifiers applied, main key pressed/released, modifiers cleared).
2. **Given** a constructed engine, **When** the author calls `hotkey` with the same arguments, **Then** behavior matches `key_click`.
3. **Given** a constructed engine, **When** the author uses only `*keys` style arguments (no combined string form), **Then** the API accepts and documents that style as the supported chord form.

---

### Edge Cases

- Drag interrupted by failure after button down: device stop-on-close MUST release held buttons; authors SHOULD still prefer paired completion of drag.
- Scroll notches that would exceed the device clamp: magnitude MUST be clamped to the legacy safe range (±127) rather than silently wrapping.
- Double-click with only one of `x`/`y` provided: MUST fail clearly (both required or both omitted).
- `hotkey` / `key_click` with empty keys: MUST fail clearly.
- Coordinates for drag/double-click follow the same hwnd vs screen rules as move; invalid hwnd fails clearly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `control` MUST provide `drag(x1, y1, x2, y2, *, button="L", duration=None, spread=10.0)` that moves to the start point, presses the selected mouse button, moves to the end point using the same humanize/duration/spread rules as `move`, then releases the button. Default button is left; right MUST be supported. Default `spread` MUST match `move` (10.0).
- **FR-002**: Between button-down and the drag move, the implementation MUST apply a short human-like pause consistent with existing click timing (tens of milliseconds order).
- **FR-003**: `control` MUST provide `scroll(direction, notches=1)` where `direction` is `"up"` or `"down"` and `notches` is a positive integer. Up maps to positive wheel delta, down to negative; one notch equals delta magnitude 1; the signed delta MUST be clamped to [-127, 127] (legacy nge behavior). Scroll MUST NOT move the pointer. Invalid direction or non-positive notches MUST fail before any device command.
- **FR-004**: Wheel scrolling MUST be a required HID capability for this feature (promote from optional documentation to a required control command used by `scroll`).
- **FR-005**: `control` MUST provide `double_click(x=None, y=None, *, hold=None, interval=None, duration=None)` for **left button only**. If both `x` and `y` are set, move first then double-click; if both omitted, double-click at current position. Exactly two full left clicks MUST be issued **at the same pointer position** (no landing-point scatter / random offset on the pre-move or between the two clicks). When `interval` is omitted, a short random gap MUST be used; when `hold` is omitted, existing click hold defaults apply. `double_click` MUST NOT accept or apply `spread`.
- **FR-006**: `key_click(*keys, hold=None)` remains the official keyboard chord API using separate key name arguments (modifiers then main key). Combined string forms such as `"ctrl+c"` MUST NOT be required or documented as supported in this feature.
- **FR-007**: `control` MUST provide `hotkey(*keys, hold=None)` as an alias with identical behavior to `key_click`.
- **FR-008**: Coordinate interpretation for drag and double-click targets MUST match existing move/click rules (client-relative when hwnd is bound; otherwise screen absolute physical pixels).
- **FR-009**: Automated tests MUST cover these APIs with a mocked HID transport; real-device smoke examples are optional/manual.
- **FR-010**: Closing the engine (or STOP on close) MUST continue to release held mouse buttons so a failed/incomplete drag does not leave the device stuck down.

### Key Entities

- **DragGesture**: Start point, end point, button, optional duration/spread; sequence press → move → release.
- **WheelScroll**: Direction, notch count; signed clamped delta sent once per call.
- **DoubleClick**: Optional target, hold, interval; two left clicks.
- **KeyChord**: Ordered key names (modifiers + main); shared by `key_click` and `hotkey`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authors can complete a documented drag from point A to B with default left button without manually sequencing down/move/up.
- **SC-002**: Authors can scroll up and down by an explicit notch count in one call; invalid counts fail 100% of the time with a clear error before device I/O.
- **SC-003**: Authors can left double-click at current position or after moving to a target using a single API call.
- **SC-004**: Authors can trigger a documented chord via both `key_click(*keys)` and `hotkey(*keys)` with matching outcomes.
- **SC-005**: Mocked HID test suite for this feature passes in CI without a physical device.

## Assumptions

- Builds on existing `001-nge2-mvp` control surface (move, button down/up, clicks, key_click, humanize, hwnd, HID mode 2).
- Wheel delta polarity and clamp match prior `nate-gaming-engine` `controller.wheel` (positive up, negative down, clamp ±127).
- Right-button double-click and horizontal/tilt wheel are out of scope.
- `"ctrl+c"` string chord parsing is out of scope.
- Short pauses for drag and double-click intervals follow the same “tens of milliseconds / random human-like” style already used for clicks.
- Firmware already understands wheel and button commands used by the prior toolkit; this feature exposes them consistently on `nge2.control`.

## Out of Scope

- OCR, YOLO, find-image.
- Foreground/background (non-HID) control backends.
- Right-button or middle-button double-click.
- Mouse wheel left/right tilt.
- New chord string DSL (`"ctrl+c"`).
- Changing existing `left_click` / `right_click` / `move_and_click` semantics except as needed for shared helpers.
