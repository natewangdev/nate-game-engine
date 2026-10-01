# 实现计划：Time 模块（sleep / delay）

**分支**：`008-time` | **日期**：2026-10-01 | **规格**：[spec.zh-CN.md](./spec.zh-CN.md)

英文权威版：[`plan.md`](./plan.md)。

## 摘要

新增无状态 `nge2.time`：`sleep` / `delay` 支持单参固定与双参闭区间均匀随机毫秒延时；模块 import、`Time` 静态方法、`engine.time` 三者等价。成功返回实际 `int` ms；非法 → `ValueError`。无新依赖；不改造 control/geom/vision 内部 sleep。

## 技术上下文

Python 3.11+；stdlib `time`/`random`；pytest + monkeypatch 缝；无 Win32 硬件依赖。

## 宪法检查

I–VII PASS。领域列表补上 `time`。

## 项目结构

与英文版相同路径列表。
