# 任务：控制手势

**输入**：`/specs/002-control-gestures/` 设计文档

**前置**：plan.md、spec.md、research.md、data-model.md、contracts/、quickstart.md

**测试**：已包含 — 规格 FR-009 / SC-005 与宪章要求 mock HID。

> 英文权威版：[`tasks.md`](./tasks.md)。执行 Spec Kit / implement 时**忽略**本中文版。

## 格式

`- [ ] [TaskID] [P?] [Story?] 描述（含路径）` — 与英文版一一对应（T001–T013）。

## 阶段一览

| 阶段 | 内容 | 任务 |
|------|------|------|
| Phase 1 Setup | 确认既有 control 表面 | T001 |
| Phase 2 Foundational | 共享校验辅助 | T002 |
| Phase 3 US1 拖拽 | 测试 + `drag` | T003–T004 |
| Phase 4 US2 滚轮 | 测试 + `scroll` | T005–T006 |
| Phase 5 US3 双击 | 测试 + `double_click` | T007–T008 |
| Phase 6 US4 热键 | 测试 + `hotkey` | T009–T010 |
| Phase 7 Polish | 文档、pytest、勾选任务 | T011–T013 |

## 建议顺序

Setup → Foundational → **drag** → scroll → double_click → hotkey → Polish。

详细条文以英文 `tasks.md` 为准（T001–T013 均已勾选完成）。
