# 快速验证：控制手势

**功能**：`002-control-gestures` | **日期**：2026-09-27

> 英文权威版：[`quickstart.md`](./quickstart.md)。执行 Spec Kit 时忽略本中文版。

## 自动化

```powershell
uv sync --extra dev
uv run pytest -q
```

期望：FakeTransport 覆盖 drag / scroll / double_click / hotkey 与英文版所列用例。

## 可选真机

拖拽、向下滚 5 格、目标处左键双击、`hotkey("ctrl","c")` 与 `key_click` 一致。细节见英文版。
