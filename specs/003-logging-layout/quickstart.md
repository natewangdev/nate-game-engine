# Quickstart: Logging Layout

**Feature**: `003-logging-layout`

Chinese companion: [`quickstart.zh-CN.md`](./quickstart.zh-CN.md).

```powershell
uv sync --extra dev
uv run pytest -q
```

Manual:

```python
import nge2
from nge2.log import get_logger

with nge2.NGE2(resource_dir=".", log_dir="logs") as engine:
    get_logger("demo").info("hello")
    get_logger("demo").error("失败示例")
# Expect logs/{date}/nge-001.log and screenshot/*.jpg on ERROR
```
