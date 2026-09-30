# Contract: Vision wait/poll Public API

**Feature**: `007-vision-wait`

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

```text
engine.ocr.find_text(
    text: str,
    *,
    region=None,
    multi: bool = False,
    timeout_ms: int = 0,
    interval_ms: int = 1000,
    min_score: float = 0.0,
) -> OcrLine | None | list[OcrLine]

engine.find.find_image(
    path,
    *,
    threshold=0.7,
    region=None,
    timeout_ms: int = 0,
    interval_ms: int = 500,
) -> Match | None

engine.yolo.detect(
    *,
    conf=0.25,
    iou=0.45,
    region=None,
    class_ids=None,
    timeout_ms: int = 0,
    interval_ms: int = 500,
) -> list[Detection]
```

## Shared wait rules

- `timeout_ms == 0`: one attempt; ignore interval sleep.
- `timeout_ms > 0`: poll until success or wall-clock deadline; sleep up to `interval_ms` between attempts.
- `timeout_ms > 0` and (`interval_ms <= 0` or `timeout_ms < interval_ms`) → `FindError`.
- Fresh grab each attempt.
- Blank `find_text` query → `FindError`.

## Success predicates

| API | Success |
|-----|---------|
| find_text multi=False | not None |
| find_text multi=True | non-empty list |
| find_image | Match is not None |
| detect | non-empty list |

## Timeout miss

| API | Return |
|-----|--------|
| find_text multi=False | `None` |
| find_text multi=True | `[]` |
| find_image | `None` |
| detect | `[]` |
