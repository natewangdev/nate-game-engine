# Research: Window ops

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. Enumeration & title match

- **Decision**: `EnumWindows` + `IsWindowVisible` + `GetWindowTextW` + `GetWindowRect`; filter titles with casefold substring; skip empty titles.
- **Rationale**: Matches locked clarifications (visible top-level, case-insensitive substring).
- **Alternatives considered**: UI Automation — heavier dependency. Exact match — rejected by clarify.

## 2. Activate

- **Decision**: Restore if minimized (`ShowWindow(SW_RESTORE)`), then `SetForegroundWindow`; on failure raise `WindowError` (no silent success). Optional `BringWindowToTop` as supporting call when useful.
- **Rationale**: Spec requires clear error on OS focus refusal.
- **Alternatives considered**: AttachThreadInput tricks — may improve success rate but is fragile; keep simple path first; document OS limits.

## 3. Topmost

- **Decision**: `SetWindowPos` with `HWND_TOPMOST` / `HWND_NOTOPMOST` and `SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE`.
- **Rationale**: Separates pin from activate per clarify A.
- **Alternatives considered**: Toggle-only API — rejected.

## 4. Move (outer frame)

- **Decision**: Read current size via `GetWindowRect`; `SetWindowPos` / `MoveWindow` to `(x, y)` keeping width/height; screen physical pixels.
- **Rationale**: Clarify B (outer top-left, no resize).
- **Alternatives considered**: Client-origin move — rejected (conflicts with control client coords).

## 5. Testing seam

- **Decision**: Module-level helpers (`_list_visible_toplevel`, `_activate_hwnd`, `_set_topmost_hwnd`, `_move_hwnd`) called by `Window` methods so unit tests monkeypatch without a real desktop.
- **Rationale**: Constitution II/III — CI without interactive UI.

## 6. Dependencies

- **Decision**: No new packages.
- **Rationale**: Constitution IV.
