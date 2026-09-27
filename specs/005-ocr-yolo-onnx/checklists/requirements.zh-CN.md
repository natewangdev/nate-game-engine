# 规格质量清单：OCR 与 YOLO（ONNX Runtime）

**目的**：规划前校验规格完整性  
**创建**：2026-09-27  
**功能**：[spec.zh-CN.md](../spec.zh-CN.md)

英文权威版：[`requirements.md`](./requirements.md)。

## 内容质量

- [x] 无阻塞规划的实现细节（张量布局留给 plan；公开 Python API 已规定）
- [x] 聚焦库契约与用户价值
- [x] 面向 nge2 集成作者
- [x] 强制章节齐全

## 需求完整性

- [x] 无残留 [NEEDS CLARIFICATION]
- [x] 需求可测
- [x] 成功标准可度量
- [x] 范围边界明确
- [x] 与 find/move 坐标规则关系明确
- [x] 已注明取代 MVP FR-015 空壳行为

## 备注

与英文版 Notes 等价（OCR 已修订为 RapidOCR；构造期加载；无需默认 OCR 模型路径）。
