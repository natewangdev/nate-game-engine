# Contract: Time Public API

**Feature**: `008-time`

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

```text
# Module
from nge2.time import sleep, delay, Time

sleep(ms: int) -> int
sleep(min_ms: int, max_ms: int) -> int
delay(...) -> int   # identical to sleep

Time.sleep(...) -> int
Time.delay(...) -> int

# Engine
engine.time.sleep(...) -> int
engine.time.delay(...) -> int
```

## Semantics

| Call | Behavior | Return |
|------|----------|--------|
| `sleep(ms)` | Sleep fixed `ms` ms | `ms` |
| `sleep(min_ms, max_ms)` | Sleep `d ~ Uniform{min_ms..max_ms}` inclusive | `d` |
| `sleep(0)` | No meaningful wait | `0` |
| `min_ms == max_ms` | Same as fixed | that value |

## Validation → `ValueError`

- Wrong arity (0 args, >2 args)
- Negative any duration
- `min_ms > max_ms`
- Non-`int` (including `bool`, `float`, `str`)

## Equivalence

Module function, `Time.*`, and `engine.time.*` MUST share the same implementation path (no divergent logic or instance RNG/state).
