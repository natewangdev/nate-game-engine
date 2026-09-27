# 契约：公开控制手势 API（`nge2.control`）

**功能**：`002-control-gestures` | **日期**：2026-09-27

> 英文权威版：[`public-api.md`](./public-api.md)。执行 Spec Kit 时忽略本中文版。

与英文版信息等价：新增 `drag` / `scroll` / `double_click` / `hotkey`；正式化 `key_click(*keys)`；`drag` 默认 `spread=10.0`（与 `move` 一致）；`double_click` **无** `spread`，两次点击同一点；错误表与非目标一致。
