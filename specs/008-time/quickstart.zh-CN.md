# 快速开始：Time 模块

**功能**：`008-time`  
英文权威版：[`quickstart.md`](./quickstart.md)。

```python
from nge2.time import sleep, delay, Time
sleep(50)
sleep(10, 30)
Time.sleep(0)
# engine.time.sleep(...) 需已构造 NGE2
```

```powershell
uv run python examples/time_smoke.py
uv run pytest tests/unit/test_time.py -q
```

纯 import/`Time` 路径无需 ESP32。
