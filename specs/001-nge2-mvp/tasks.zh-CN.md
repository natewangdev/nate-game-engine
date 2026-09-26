# 任务：nge2 MVP 核心引擎

**输入**：`/specs/001-nge2-mvp/` 设计文档

**前置**：plan.md、spec.md、research.md、data-model.md、contracts/、quickstart.md

**测试**：已包含 — 规格 FR-017 与宪章要求 CI 使用 mock 串口/截屏。

> 英文权威版：[`tasks.md`](./tasks.md)。执行 Spec Kit / implement 时**忽略**本中文版。

## 格式

`- [ ] [TaskID] [P?] [Story?] 描述（含路径）` — 与英文版任务一一对应（T001–T040）。

## 阶段一览

| 阶段 | 内容 | 任务 |
|------|------|------|
| Phase 1 Setup | 移除旧包、建 `src/nge2`、pyproject、测试目录、README | T001–T005 |
| Phase 2 Foundational | log、空壳、错误、端口登记、NGE2 骨架、导出 | T006–T012 |
| Phase 3 US1 截屏 | capture grab/release/重建 + 测试 | T013–T017 |
| Phase 4 US2 HID | keymap/transport/geom/control + 测试 | T018–T026 |
| Phase 5 US3 窗口 | DPI、客户区坐标、window API | T027–T031 |
| Phase 6 US4 日志/关闭 | mode 0/1、close、日志文件 | T032–T035 |
| Phase 7 Polish | 版本测试、ruff、README、pytest、真机备忘 | T036–T040 |

## 独立验收（与英文版相同）

- **US1**：假 capture（及假 HID）下 grab/区域/release 后再 grab；后端不可用构造失败  
- **US2**：假 transport 下 move/click/keys；无设备/端口忙构造失败  
- **US3**：坐标换算与 hwnd 相对移动  
- **US4**：mode 0/1 失败、日志文件、close 后不可用  

## 建议 MVP 顺序

Setup → Foundational → **US1** → **US2** → US3 → US4 → Polish  

详细任务条文以英文 `tasks.md` 为准（实现后 T001–T040 均已勾选完成）。
