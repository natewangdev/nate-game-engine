# 数据模型：Time 模块

**功能**：`008-time`  
英文权威版：[`data-model.md`](./data-model.md)。

## 实体

- **DurationMs**：非负整数毫秒（入参与成功返回值）。
- **RandomDelayRange**：`min_ms <= max_ms`；闭区间均匀抽样。
- **Time**：无状态门面；`engine.time` 仅属性访问。
