# 契约：Time 公开 API

**功能**：`008-time`  
英文权威版：[`public-api.md`](./public-api.md)。

```text
from nge2.time import sleep, delay, Time
sleep(ms) / sleep(min_ms, max_ms) -> int
delay 同 sleep
Time.sleep / Time.delay
engine.time.sleep / engine.time.delay
```

非法参数 → `ValueError`；三表面等价；无实例状态。
