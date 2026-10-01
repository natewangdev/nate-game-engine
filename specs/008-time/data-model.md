# Data Model: Time module

**Feature**: `008-time`

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

## Entities

### DurationMs

- **Type**: non-negative `int` (milliseconds)
- **Role**: argument(s) to `sleep`/`delay` and success return value
- **Constraints**: `>= 0`; not `bool`; not float/str

### RandomDelayRange

- **Fields**: `min_ms: DurationMs`, `max_ms: DurationMs`
- **Invariant**: `min_ms <= max_ms`
- **Sample**: one `DurationMs` uniformly from closed integer interval

### Time (facade)

- **State**: none (stateless)
- **Methods**: `sleep`, `delay` (static or unbound-equivalent)
- **Engine**: `engine.time` holds a `Time` instance for attribute access only

No persistence, identity, or lifecycle beyond process lifetime.
