# 数据模型：nge2 MVP 核心引擎

**功能**：`001-nge2-mvp` | **日期**：2026-09-26

> 英文权威版：[`data-model.md`](./data-model.md)。执行 Spec Kit 时忽略本中文版。

仅进程内实体（无持久化数据库）。字段、校验与状态机与英文版信息等价。

## 实体概要

- **NGE2**：资源目录、截屏后端、hwnd、humanize、control_mode、closed；拥有 Capture / Control / Window。
- **CaptureSession**：后端名、是否活跃；`grab` / `release`；release 后 grab 重建。
- **ControlSession（HID）**：端口、指针位置、屏幕尺寸；键鼠 API（含左右键点击与按下/抬起）。
- **WindowBinding**：hwnd、标题、客户区本地/屏幕矩形。
- **HumanizePath**：路点与 spread。
- **KeyBinding**：友好名 ↔ Usage ID / 修饰键。
- **StubModule**：`find`/`ocr`/`yolo` 无状态，能力调用抛 `NotImplementedError`。

## 生命周期

`NGE2`：构造成功 → ACTIVE → close/`with` → CLOSED。  
Capture：ACTIVE → release → IDLE → grab → ACTIVE。  
HID 端口登记：free → open → held → close → free。
