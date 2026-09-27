# Feature Specification: Find Image and Find Color

**Feature Branch**: `004-find-vision`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "Implement find module: find_image / find_images with resource_dir-relative templates, threshold (default 0.7), optional region (client-relative if hwnd else screen; omit = full client or full first display), NMS for multi; find_color with RGB/#hex + tolerance + region + multi; fresh capture.grab each call; Match coords align with move; missing template FileNotFoundError; color miss returns None."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

**Supersedes (partial)**: `001-nge2-mvp` FR-014 (find stub only). After this feature, find-image/find-color behavior defined here is authoritative.

## Clarifications (locked)

| Topic | Decision |
|-------|----------|
| API shape | **C**: `find_image` (best single) + `find_images` (multi) |
| Coordinate space | **A**: Same as `control.move` (hwnd → client-relative; else screen absolute) |
| Threshold | Default **0.7**; parameter name **`threshold`** |
| Multi-match | Non-maximum suppression / non-overlapping boxes (legacy `find_all` style) |
| Frame source | Every find call performs a fresh `capture.grab` (no stale cached frame) |
| Color API | `(R,G,B)` or `"#RRGGBB"` + `tolerance` + optional `region` + `multi`; miss → **`None`** (or empty list when multi) |
| Missing template | Raise **`FileNotFoundError`** |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find a single template image (Priority: P1)

A script author calls `engine.find.find_image("templates/btn.png", threshold=0.7)` (path relative to `resource_dir`). The engine grabs a fresh frame, searches the full client area (if hwnd bound) or first display (if not), or an optional region, and returns the best match center if score ≥ threshold, else `None`.

**Why this priority**: Core vision primitive for UI automation.

**Independent Test**: FakeCapture with a synthetic frame + known template patch; assert Match center/score; assert missing file raises FileNotFoundError; assert low threshold miss returns None.

**Acceptance Scenarios**:

1. **Given** a bound hwnd and a template under `resource_dir`, **When** `find_image` is called without region, **Then** search uses the full client area and returns client-relative center coordinates on success.
2. **Given** no hwnd, **When** `find_image` is called without region, **Then** search uses the full first-display frame and returns screen absolute coordinates.
3. **Given** an optional `region=(x1,y1,x2,y2)`, **When** find runs, **Then** only that rectangle is searched (interpreted per hwnd rules).
4. **Given** best score &lt; `threshold`, **When** `find_image` returns, **Then** result is `None`.
5. **Given** a missing template file, **When** `find_image` is called, **Then** `FileNotFoundError` is raised.
6. **Given** two successive finds, **When** each is called, **Then** each triggers its own `capture.grab` (fresh frame).

---

### User Story 2 - Find multiple template matches (Priority: P1)

A script author calls `engine.find.find_images(...)` to get all non-overlapping matches above threshold, ordered by score descending (or stable documented order).

**Why this priority**: Needed for listing repeated UI icons.

**Independent Test**: Synthetic frame with two non-overlapping copies; assert two Matches; overlapping peaks suppressed.

**Acceptance Scenarios**:

1. **Given** multiple instances above threshold, **When** `find_images` runs, **Then** each non-overlapping match is returned with center coordinates in the move-aligned space.
2. **Given** no matches above threshold, **When** `find_images` runs, **Then** an empty list is returned.

---

### User Story 3 - Find color (Priority: P2)

A script author finds pixels matching a color within tolerance inside an optional region (same region rules as find image).

**Why this priority**: Complements template matching for simple markers.

**Independent Test**: Fake frame with known RGB blob; assert single and multi results; miss → None / [].

**Acceptance Scenarios**:

1. **Given** `color=(R,G,B)` or `"#RRGGBB"` and `tolerance`, **When** `find_color(..., multi=False)` finds a hit, **Then** return a color-match result with move-aligned `(x,y)` (documented fields).
2. **Given** no pixel within tolerance, **When** `find_color` runs with `multi=False`, **Then** return `None`.
3. **Given** `multi=True`, **When** matches exist, **Then** return a list (empty if none).
4. **Given** region/hwnd rules, **When** color find runs, **Then** region interpretation matches find-image rules.

---

### Edge Cases

- Template larger than search region → no match / empty (must not crash).
- Invalid region (x2≤x1 or y2≤y1) → clear error (`FindError` or `ValueError`).
- Invalid color string → clear error before grab when possible.
- Capture failure during find → propagate capture/construct-style error clearly (not silent None).
- Paths with non-ASCII characters on Windows must load (legacy np.fromfile / imdecode pattern).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Public APIs MUST be `engine.find.find_image` and `engine.find.find_images` (and `find_color`), replacing stub `NotImplementedError` behavior for these entrypoints.
- **FR-002**: Template paths MUST be resolved relative to the engine `resource_dir`. Absolute paths MAY be accepted if provided.
- **FR-003**: `threshold` MUST default to `0.7`. Matches below threshold MUST NOT be returned as successes.
- **FR-004**: Optional `region=(x1,y1,x2,y2)` MUST use client-relative coords when hwnd is set, else screen absolute; omitted region MUST mean full client (hwnd) or full first-display frame (no hwnd).
- **FR-005**: Returned match centers MUST use the same coordinate space as `control.move` targets.
- **FR-006**: `find_image` MUST return the single best match as a structured Match (center x/y, score, width, height) or `None`.
- **FR-007**: `find_images` MUST return all matches above threshold after non-overlapping suppression; empty list if none.
- **FR-008**: Each find call MUST obtain a fresh frame via this engine’s `capture.grab` (full or cropped as needed).
- **FR-009**: Missing template file MUST raise `FileNotFoundError`.
- **FR-010**: `find_color(color, *, tolerance=10, region=None, multi=False)` MUST accept `(R,G,B)` or `"#RRGGBB"`; on miss return `None` (single) or `[]` (multi).
- **FR-011**: Default install MUST include runtime deps needed for template matching (e.g. OpenCV), per constitution full-install rule; justify in plan.
- **FR-012**: Automated tests MUST cover find with FakeCapture / synthetic arrays without a physical display.

### Key Entities

- **Match**: `x`, `y` (center), `score`, `width`, `height`.
- **ColorMatch**: at least `x`, `y`; MAY include sampled color / count.
- **SearchRegion**: optional rect + hwnd-aware interpretation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authors can find a template by resource-relative path and click its center via `move`/`move_and_click` without manual coordinate conversion when hwnd is set.
- **SC-002**: `find_images` returns multiple non-overlapping hits for repeated icons in a documented fixture.
- **SC-003**: Missing template raises `FileNotFoundError` in 100% of such calls.
- **SC-004**: Color miss returns `None` / `[]` without throwing.
- **SC-005**: CI find tests pass with fakes (no real game window required).

## Assumptions

- Matching algorithm is normalized cross-correlation style template match (OpenCV `TM_CCOEFF_NORMED` or equivalent).
- First-display-only capture limitation from MVP still applies when no hwnd / fullscreen search.
- `tolerance` for color is per-channel absolute difference unless plan documents otherwise.
- Multi color find MAY cap results (e.g. max 500) to avoid huge lists; document in plan if capped.

## Out of Scope

- OCR / YOLO (see `005-ocr-yolo-onnx`)
- Scale/rotation-invariant matching beyond basic template match
- Caching frames across find calls
- GPU-accelerated search
