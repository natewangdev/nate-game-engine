# 研究：Time 模块

**功能**：`008-time`  
英文权威版：[`research.md`](./research.md)。

## 决策摘要

三表面（模块 / `Time` 静态 / `engine.time`）；`self.time = Time()` 无开闭门禁；`random.randint` + `time.sleep` 可测缝；拒绝 `bool`/浮点；`delay` 别名；仅 `ValueError`；constitution 领域列表加 `time`。
