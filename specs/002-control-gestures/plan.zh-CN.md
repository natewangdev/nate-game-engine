# 实现计划：控制手势

**分支**：`002-control-gestures` | **日期**：2026-09-27 | **规格**：[spec.md](./spec.md)

**输入**：`/specs/002-control-gestures/spec.md`

> 英文权威版：[`plan.md`](./plan.md)。执行 Spec Kit 时忽略本中文版。

## 摘要

在 `001-nge2-mvp` 既有 HID 表面上扩展 `nge2.control`：`drag`、`scroll`（旧 nge ±1 / ±127）、仅左键 `double_click`、`hotkey` 作为 `key_click(*keys)` 别名。无新运行时依赖。本功能契约将 `WHEEL` 升为必需；用 `FakeTransport` 测命令序列。

## 技术上下文

与英文版等价：Python 3.11+、沿用现有依赖、pytest + FakeTransport、Windows、库增量、无新依赖、坐标/拟人规则同 move。

## 宪章检查

与英文版门禁表一致：I–VII 均为 PASS；设计后复检 PASS。

## 项目结构

文档与源码树与英文 `plan.md` 信息等价；实现集中在 `src/nge2/control/__init__.py` 与契约测试。

## 复杂度跟踪

无宪章违规需辩护。
