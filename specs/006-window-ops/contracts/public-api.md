# Contract: Window Public API (ops)

**Feature**: `006-window-ops`

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

## Types

```text
WindowMatch
    hwnd: int
    title: str
    rect: tuple[int, int, int, int]  # outer frame screen LTRB
```

## `engine.window` (additive)

```text
find_by_title(query: str) -> list[WindowMatch]
activate(hwnd: int | None = None) -> None
set_topmost(enabled: bool, hwnd: int | None = None) -> None
move(x: int, y: int, hwnd: int | None = None) -> None
```

### Semantics

| API | Notes |
|-----|-------|
| find_by_title | Visible top-level only; case-insensitive substring; empty list if none; blank query → `WindowError`; does not change bound hwnd |
| activate | Foreground focus for target; OS refusal → `WindowError` |
| set_topmost | `True` = always-on-top; `False` = clear; does not imply activate |
| move | Outer-frame top-left `(x,y)` screen physical pixels; size unchanged; not client-relative |

### Target hwnd

Optional `hwnd` on activate / set_topmost / move: if omitted, use bound hwnd; if both missing → `WindowError`. Explicit hwnd never rebinds `engine.window.hwnd`.

### Errors

| Condition | Type |
|-----------|------|
| Blank find query | `WindowError` |
| Missing target hwnd | `WindowError` |
| Invalid / destroyed hwnd | `WindowError` |
| OS activate / setpos failure | `WindowError` |

### Unchanged (MVP)

`hwnd`, `title`, `client_region`, `client_to_screen`, `screen_to_client`
