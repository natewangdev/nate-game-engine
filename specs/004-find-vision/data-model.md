# Data Model: Find

**Feature**: `004-find-vision`

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

## Match

| Field | Type | Notes |
|-------|------|-------|
| x, y | int | Center; move-aligned space |
| score | float | [0,1] |
| width, height | int | Template size |

## ColorMatch

| Field | Type | Notes |
|-------|------|-------|
| x, y | int | Move-aligned |
| color | tuple[int,int,int] | Requested RGB |

## SearchContext

resource_dir, hwnd/window, capture, optional region → screen crop rect + return-space transform.
