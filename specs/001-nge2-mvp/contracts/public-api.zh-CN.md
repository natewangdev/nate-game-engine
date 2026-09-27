# 契约：公开 Python API（`nge2`）

**功能**：`001-nge2-mvp` | **日期**：2026-09-26

> 英文权威版：[`public-api.md`](./public-api.md)。执行 Spec Kit 时忽略本中文版。

与英文版信息等价：`NGE2` 构造参数、`capture`/`control`/`window`/`log` 表面、空壳 `NotImplementedError`、构造/使用错误表。`control` 含 `left_down` / `left_up` / `right_down` / `right_up`（`BTN`）以及完整点击（`CLK`）。`move` 与相关移动 API 默认 `spread=10.0`。`geom` 不作为稳定公开 API。
