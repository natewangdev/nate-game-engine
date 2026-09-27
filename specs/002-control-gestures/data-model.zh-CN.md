# 数据模型：控制手势

**功能**：`002-control-gestures` | **日期**：2026-09-27

> 英文权威版：[`data-model.md`](./data-model.md)。执行 Spec Kit 时忽略本中文版。

仅进程内请求参数实体（无持久化），与英文版字段/校验/生命周期信息等价：

- **DragGesture**：起终点、button、duration/spread；move→按下→停顿→move→抬起。
- **WheelScroll**：direction、notches → 钳制后的 delta；单次 WHEEL。
- **DoubleClick**：可选 x/y、hold、interval；预移动无散布；两次 CLK L 同一点。
- **KeyChord**：`key_click` 与 `hotkey` 共用。
