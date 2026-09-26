# 实现计划：nge2 MVP 核心引擎

**分支**：`001-nge2-mvp` | **日期**：2026-09-26 | **规格**：[spec.zh-CN.md](./spec.zh-CN.md)

**输入**：来自 `/specs/001-nge2-mvp/spec.md` 的功能规格

> 英文权威版：[`plan.md`](./plan.md)。执行 Spec Kit 时忽略本中文版。

## 摘要

将包重建为可 import 的 `nge2`，以实例中心的 `NGE2` 门面拥有每实例截屏（`dxcam` 或 `mss`）、ESP32-S3 HID 控制（串口行协议）、内部拟人几何、窗口客户区映射（DPI aware）与日志。MVP 实现 capture + HID control + geom + window + log；`find`/`ocr`/`yolo` 以可 import 空壳交付。行为契约对齐既有 `nate-gaming-engine`，但不作为依赖引入。

## 技术上下文

**语言/版本**：Python 3.11+

**主要依赖**：`numpy`；`dxcam` + `mss`；`pyserial`；标准库 `ctypes`/`logging`。MVP 空壳不需要 OCR/YOLO 运行时。

**存储**：不适用（进程内；可选 cwd 下日志文件）

**测试**：`pytest`；纯逻辑单测；CI mock 串口/截屏；真机/真屏可选标记

**目标平台**：Windows（主）；非 Windows 非范围

**项目类型**：Python 库（`src/`），PyPI `nate-game-engine`，import `nge2`

**性能目标**：典型桌面约 5 秒内完成构造 + 全屏 grab（不含冷安装）；HID 路点速率对齐既有拟人实现

**约束**：物理像素 / DPI aware；仅第一块显示器；截屏后端不自动回退；每端口仅一个 HID 占用者；默认全量安装

**规模**：单包 MVP（约 8 模块）；多引擎实例允许独立 capture；HID 按端口互斥

## 宪章检查

| 门禁 | 状态 | 说明 |
|------|------|------|
| I. 库优先 `src/nge2/` | PASS | 实例 API |
| II. 副作用隔离 | PASS | 窄接口 + 可 mock |
| III. 测试纪律 | PASS | pytest + mock CI |
| IV. 全量安装 & YAGNI | PASS | 无 extras；无投机分层 |
| V. SemVer / Windows | PASS | 已声明 |
| VI–VII. 双语 | PASS | 成对产物 |

**设计后复核**：PASS。

## 项目结构

（与英文版 `plan.md` 中的目录树信息等价；实现以英文版路径为准。）

**结构决策**：单库 `src/nge2` 八模块；HID 辅助放在 `control/` 私有；实现时移除 `src/nate_game_engine/`。

## 复杂度跟踪

无需要正当化的宪章违规。
