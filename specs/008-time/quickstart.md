# Quickstart: Time module

**Feature**: `008-time`

Chinese companion: [`quickstart.zh-CN.md`](./quickstart.zh-CN.md).

## Import (no hardware)

```python
from nge2.time import sleep, delay, Time

slept = sleep(50)          # fixed 50 ms; returns 50
slept = sleep(10, 30)      # random in [10, 30]; returns actual
assert delay is sleep or delay(0) == 0
assert Time.sleep(0) == 0
```

## Engine surface

```python
# With a constructed NGE2 (hardware or test fakes):
engine.time.sleep(20)
engine.time.delay(5, 15)
```

## Example script

```powershell
uv run python examples/time_smoke.py
```

No ESP32 required for the import/`Time` paths in the smoke script.

## Tests

```powershell
uv run pytest tests/unit/test_time.py -q
```
