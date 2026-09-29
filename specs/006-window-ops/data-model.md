# Data Model: Window ops

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

## WindowMatch

| Field | Type | Rules |
|-------|------|-------|
| hwnd | int | Non-zero window handle |
| title | str | Window title at enumeration time |
| rect | `(left, top, right, bottom)` | Outer-frame screen physical pixels; `right > left`, `bottom > top` when valid |

Immutable value object (frozen dataclass).

## Window target resolution

| Input | Result |
|-------|--------|
| `hwnd=` explicit int | Use that hwnd; bound hwnd unchanged |
| `hwnd=None` and bound set | Use `Window.hwnd` |
| `hwnd=None` and bound `None` | `WindowError` |

Blank / whitespace-only find query → `WindowError`.

## Relationships

- `NGE2.window` owns one `Window` instance with optional bound hwnd (construct-time).
- `find_by_title` → `list[WindowMatch]`; does not mutate binding.
- activate / set_topmost / move operate on resolved target only.
