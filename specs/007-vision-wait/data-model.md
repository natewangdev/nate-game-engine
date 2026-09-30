# Data Model: Vision wait/poll

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

## WaitParams (conceptual)

| Field | Type | Rules |
|-------|------|-------|
| timeout_ms | int | `>= 0`; `0` = one attempt |
| interval_ms | int | When `timeout_ms > 0`: must be `> 0` and `<= timeout_ms` |

## find_text result

| multi | Hit | Miss / timeout |
|-------|-----|----------------|
| False | `OcrLine` | `None` |
| True | `list[OcrLine]` | `[]` |

Entities `OcrLine`, `Match`, `Detection` unchanged from 004/005.
