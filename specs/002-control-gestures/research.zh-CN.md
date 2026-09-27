# 研究：控制手势

**功能**：`002-control-gestures` | **日期**：2026-09-27

> 英文权威版：[`research.md`](./research.md)。执行 Spec Kit 时忽略本中文版。

## 结论摘要（与英文版等价）

1. **拖拽**：`move(起点)` → `BTN` 按下 → 短停顿 → `move(终点)` → `BTN` 抬起；复用既有 `_button`/`move`。
2. **滚轮**：对齐旧 nge：`WHEEL ±notches`，钳制 [-127,127]；非法方向/格数发送前失败。
3. **双击**：仅左键；预移动 `spread=0` 精确落点；两次 `CLK L` 同一位置；无 `spread` 参数；x/y 须都给或都不给。
4. **hotkey**：委托 `key_click(*keys)`；不做 `"ctrl+c"`。
5. **契约**：本功能目录下增量契约；`WHEEL` 标为必需。
6. **测试**：FakeTransport 契约测试覆盖命令序列。
