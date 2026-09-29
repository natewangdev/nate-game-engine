# 实现计划：窗口激活、置顶、移动与按标题查找

**分支**：`006-window-ops` | **日期**：2026-09-29 | **规格**：[spec.zh-CN.md](./spec.zh-CN.md)

英文权威版：[`plan.md`](./plan.md)。

## 摘要

扩展 `engine.window`：`find_by_title`、`activate`、`set_topmost(bool)`、`move(x, y)`（外框屏幕物理像素、不改大小）。默认绑定 hwnd 或显式 hwnd；不改绑。复用 `WindowError`。无新运行时依赖（`ctypes`）。

## 技术上下文

与英文版等价：Python 3.11+、ctypes user32、pytest + 假对象、Windows、库增量、无新依赖。

## 宪章检查

与英文版表一致（I–VII PASS）。

## 项目结构

与英文版路径树等价。

## 复杂度跟踪

无。
