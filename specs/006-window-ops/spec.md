# Feature Specification: Window activate, topmost, move, and find-by-title

**Feature Branch**: `006-window-ops`

**Created**: 2026-09-29

**Status**: Draft

**Input**: User description: "Extend the window module with activate, topmost, move, and find-by-title (list). Design parameters and returns to fit existing specs."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

**Extends**: `001-nge2-mvp` FR-011 (window queries: bound hwnd, title, client region). Existing query properties remain; this feature adds window management and discovery APIs. After this feature lands, behavior defined here is authoritative for those new APIs.

## Clarifications (locked)

### Session 2026-09-29

| Topic | Decision |
|-------|----------|
| Target / rebind model | **B**: `find_by_title` returns a list only; activate / set_topmost / move default to the bound hwnd and MAY accept an explicit `hwnd`; operations MUST NOT auto-rebind the engine hwnd |
| Topmost semantics | **A**: Set or clear always-on-top via a boolean; separate from activate (foreground focus) |
| Move semantics | **B**: Position only (no resize); `(x, y)` is the **outer frame** top-left in **screen physical pixels** |
| Title match | **B**: Case-insensitive substring containment |
| Find results | **A**: Visible top-level windows only; each item includes `hwnd`, `title`, and outer-frame screen rect `(left, top, right, bottom)` |

- Q: Target model for ops vs find? → A: **B** (list + optional hwnd; no auto-rebind).
- Q: Topmost behavior? → A: **A** (`set_topmost(bool)`; separate from activate).
- Q: Move position meaning? → A: **B** (outer-frame screen physical pixels; no resize).
- Q: Title matching? → A: **B** (case-insensitive substring).
- Q: Enumerated windows and fields? → A: **A** (visible top-level; hwnd + title + outer rect).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find windows by title (Priority: P1)

A script author searches for visible top-level windows whose titles contain a query string (case-insensitive). They receive a list of matches with handles, titles, and outer-frame screen rectangles, then pass a chosen `hwnd` into other window APIs without changing the engine’s bound hwnd.

**Why this priority**: Discovery is the prerequisite for operating on windows that were not bound at construct time.

**Independent Test**: Fake or stubbed desktop enumeration returning known titles; assert match filter, empty list, and returned fields. No real game window required for unit/CI.

**Acceptance Scenarios**:

1. **Given** at least one visible top-level window whose title contains `"notepad"` (any case), **When** the author calls find-by-title with `"Note"`, **Then** that window appears in the result list with `hwnd`, `title`, and outer-frame screen rect.
2. **Given** no visible top-level title contains the query, **When** find-by-title runs, **Then** an empty list is returned (not an error).
3. **Given** multiple matching visible top-level windows, **When** find-by-title runs, **Then** all matches are returned (order MAY be enumeration order; MUST be deterministic for a stable desktop snapshot in tests).
4. **Given** a successful find, **When** results return, **Then** the engine’s bound `hwnd` is unchanged.

---

### User Story 2 - Activate a window (Priority: P1)

A script author brings a window to the foreground (focus / Z-order front) using either the engine’s bound hwnd or an explicit hwnd from find results.

**Why this priority**: Scripts often need the target game or tool in front before capture or human observation; distinct from always-on-top.

**Independent Test**: With a bound or injected hwnd double, call activate; assert the OS-facing “activate” request is issued for that hwnd (or a documented fake records the call). Failure paths raise a clear window error.

**Acceptance Scenarios**:

1. **Given** a bound hwnd, **When** activate is called without an explicit hwnd, **Then** the bound window is requested to the foreground.
2. **Given** an explicit hwnd from find (or known handle), **When** activate is called with that hwnd, **Then** that window is requested to the foreground and the bound hwnd is unchanged.
3. **Given** no bound hwnd and no explicit hwnd, **When** activate is called, **Then** a clear window error is raised before any OS call.
4. **Given** an invalid or destroyed hwnd, **When** activate is called, **Then** a clear window error is raised.

---

### User Story 3 - Set or clear always-on-top (Priority: P2)

A script author pins a window above others (`topmost=True`) or restores normal Z-order behavior (`topmost=False`), independently of activate.

**Why this priority**: Useful for overlays and monitoring; secondary to find + activate for typical bot setup.

**Independent Test**: Call set-topmost true then false on a known hwnd (or fake); assert both states are requested; unbound-without-explicit fails clearly.

**Acceptance Scenarios**:

1. **Given** a target hwnd (bound or explicit), **When** set-topmost is called with `True`, **Then** the window is requested to always-on-top.
2. **Given** a target hwnd that is always-on-top, **When** set-topmost is called with `False`, **Then** the window is requested to leave always-on-top.
3. **Given** no bound hwnd and no explicit hwnd, **When** set-topmost is called, **Then** a clear window error is raised.

---

### User Story 4 - Move window outer frame (Priority: P2)

A script author repositions a window by setting its **outer frame** top-left to screen physical-pixel coordinates, without changing size.

**Why this priority**: Complements find + activate for arranging the game window; secondary to discovery/foreground.

**Independent Test**: Move to known `(x, y)`; assert outer top-left matches (or fake records requested position); size unchanged; coordinate space is screen absolute (not client-relative).

**Acceptance Scenarios**:

1. **Given** a target hwnd, **When** move is called with `(x, y)`, **Then** the window’s outer-frame top-left is at that screen physical-pixel position and width/height are unchanged.
2. **Given** a bound hwnd and client-relative control coordinates elsewhere, **When** window move uses `(x, y)`, **Then** those values are interpreted as **screen** outer-frame coordinates (not client-relative).
3. **Given** no bound hwnd and no explicit hwnd, **When** move is called, **Then** a clear window error is raised.
4. **Given** an invalid or destroyed hwnd, **When** move is called, **Then** a clear window error is raised.

---

### Edge Cases

- Blank or whitespace-only title query → raise a clear window error (do not enumerate “everything”).
- Hidden, minimized-to-tray, or non-top-level windows → excluded from find results.
- Tool/owned windows that are not top-level → excluded.
- OS refuses foreground activate (common Windows focus rules) → raise a clear window error; MUST NOT silently no-op.
- Explicit `hwnd` that does not match the bound hwnd → ops still apply to the explicit hwnd; binding unchanged.
- Closed engine → same closed-engine failure rules as other modules (`ClosedError` or equivalent already defined by MVP).
- Existing read-only queries (`hwnd`, `title`, `client_region`, coordinate helpers) remain available and behaviorally unchanged except where this feature documents additive APIs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `engine.window` MUST provide find-by-title that accepts a non-blank title query string and returns a list of matches for **visible top-level** windows whose titles contain the query as a **case-insensitive substring**.
- **FR-002**: Each find match MUST include: `hwnd` (integer handle), `title` (string), and outer-frame screen rectangle as `(left, top, right, bottom)` in physical pixels.
- **FR-003**: Find-by-title MUST NOT modify the engine’s bound hwnd.
- **FR-004**: `engine.window` MUST provide activate that brings a window to the foreground. Target hwnd is the optional explicit argument if provided; otherwise the bound hwnd. If neither is available, MUST raise a clear window error.
- **FR-005**: `engine.window` MUST provide set-topmost that accepts a boolean enabling or disabling always-on-top for the target hwnd (same default/explicit hwnd rules as FR-004). Activate and set-topmost MUST remain separate operations.
- **FR-006**: `engine.window` MUST provide move that sets the target window’s **outer-frame** top-left to `(x, y)` in **screen physical pixels** without resizing. Same default/explicit hwnd rules as FR-004. These coordinates MUST NOT be interpreted as client-relative even when a hwnd is bound.
- **FR-007**: Activate, set-topmost, and move MUST NOT auto-rebind the engine hwnd when an explicit hwnd is supplied.
- **FR-008**: Invalid, destroyed, or OS-rejected window operations MUST raise a clear window error (existing `WindowError` family or equivalent documented error type); they MUST NOT fail silently.
- **FR-009**: Existing MVP window query surface (`hwnd`, `title`, `client_region`, client↔screen helpers) MUST remain available; this feature is additive.
- **FR-010**: Automated tests MUST cover matching rules, empty results, missing-target errors, and move coordinate semantics with fakes/mocks so CI does not require a real interactive desktop. Optional manual checks MAY use real windows.

### Key Entities

- **WindowMatch**: One find result — hwnd, title, outer-frame screen rect.
- **Window target**: Either the engine’s bound hwnd or an explicit hwnd argument used by activate / set-topmost / move.
- **Window binding** (unchanged ownership): Optional hwnd set at `NGE2` construction; still used for control client-relative coordinates and query properties; not mutated by this feature’s APIs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A script author can locate a visible window by partial title and obtain its hwnd in one call without rebinding the engine.
- **SC-002**: Using that hwnd (or the bound hwnd), the author can activate, pin/unpin always-on-top, and move the outer frame to a chosen screen position in a short script (under ~10 lines of window API calls).
- **SC-003**: Missing target hwnd and blank title queries fail with clear errors in 100% of automated negative tests (no silent success).
- **SC-004**: CI unit/contract tests for match rules, empty list, and move/activate/topmost target resolution pass without a real game window.
- **SC-005**: After find or ops with an explicit hwnd, the engine’s bound hwnd reported by `engine.window.hwnd` is unchanged in automated tests.

## Assumptions

- Primary platform remains Windows (same as MVP); non-Windows out of scope.
- “Visible top-level” means windows that a normal desktop user would consider open and shown (not hidden); exact Win32 visibility flags are an implementation detail as long as acceptance scenarios hold.
- Outer-frame rectangle matches the window’s full outer bounds (including non-client chrome), consistent with common desktop “move window to x,y” expectations.
- Resize, minimize/maximize/restore, and changing the bound hwnd after construct are **out of scope** for this feature.
- Naming on the public facade MAY use clear identifiers such as `find_by_title`, `activate`, `set_topmost`, and `move` under `engine.window` (distinct from `engine.control.move`); exact signatures are finalized in the public-api contract during planning.
- Error type preference: reuse `WindowError` where it already exists for window failures.

## Out of Scope

- Rebinding `NGE2` hwnd after construction.
- Moving by client-area origin or by relative delta.
- Changing window size or show state (min/max/restore).
- Regex or wildcard title matching.
- Enumerating child/controls or invisible windows.
- Non-Windows platforms.
