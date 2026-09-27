# 功能规格：OCR（RapidOCR）与 YOLO（ONNX Runtime）

**功能分支**：`005-ocr-yolo-onnx`

**创建**：2026-09-27

**状态**：草稿

**输入**：OCR 改回旧库 RapidOCR 方式；YOLO 仍用 onnxruntime；二者均在 `NGE2` 构造时加载；每实例唯一一套。

英文权威版：[`spec.md`](./spec.md)。

**部分取代**：`001-nge2-mvp` FR-015（OCR/YOLO 空壳）。本功能落地后以本文为准。

## 澄清（已锁定）

### Session 2026-09-27

加载时机、YOLO CPU ORT、坐标/region、`FindError`、分数降序、OCR `box` 必填、过小区域 `[]`、`close` 释放等与英文版表一致。

### Session 2026-09-27（OCR 后端修订）

| 主题 | 决策 |
|------|------|
| OCR 技术栈 | **RapidOCR**（对齐旧 `nate-gaming-engine`），不再用手写 det+rec ORT |
| OCR 加载时机 | 仍在 **`NGE2` 构造时**创建 RapidOCR 引擎（与 YOLO 一致） |
| OCR 模型路径 | **默认不需要**；RapidOCR 自带/下载默认模型；可用 `ocr_kwargs` 覆盖 |
| 移除 | 以 `ocr_det` / `ocr_rec` / `ocr_keys` 作为主路径的 API 要求 |

- Q: OCR 是否改回 RapidOCR 且仍构造期加载？ → A: **是**。

## 用户场景与测试

### 用户故事 1 - 构造加载（P1）

构造时初始化 RapidOCR + 加载 YOLO；缺 YOLO 或 RapidOCR 初始化失败 → `ConstructError`；默认无需 OCR 模型路径。

### 用户故事 2 - YOLO（P1）

与英文版等价（现场 grab、region、conf/iou、move 坐标、分数降序）。

### 用户故事 3 - RapidOCR 识别（P1）

`engine.ocr.recognize`；必填 `box` + 中心；无文本 `[]`；分数降序。

### 边界情况

与英文版等价（含 close 后 `ClosedError`）。

## 功能需求

与英文版 FR-001–FR-016（含 FR-002b）及公开表面等价：

```text
yolo_model / yolo_names? / ocr_kwargs?
engine.ocr.recognize(*, region=None) -> list[OcrLine]
engine.yolo.detect(*, conf=0.25, iou=0.45, region=None, class_ids=None) -> list[Detection]
```

默认安装含 RapidOCR（ORT 后端）与 CPU `onnxruntime`；YOLO 权重不随包装。

## 成功标准 / 假设 / 范围外

与英文版 SC-001–SC-006、Assumptions、Out of Scope 等价。
