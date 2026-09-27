# 功能规格：找图与找色

**功能分支**：`004-find-vision`

**创建**：2026-09-27

**状态**：草稿

**输入**：实现 find：`find_image` / `find_images`（resource_dir 相对路径、threshold 默认 0.7、可选区域、NMS 多图）；`find_color`（RGB/#hex、tolerance、region、multi）；每次现场 grab；坐标与 move 一致；缺模板 `FileNotFoundError`；找色失败 `None`/`[]`。

> 英文权威版：[`spec.md`](./spec.md)。执行 Spec Kit 时忽略本中文版。

**部分取代**：`001-nge2-mvp` FR-014（find 仅空壳）；本功能生效后以本规格为准。

## 已锁定澄清

| 主题 | 决定 |
|------|------|
| API | **C**：`find_image`（单）+ `find_images`（多） |
| 坐标 | **A**：与 `move` 一致（有 hwnd → 客户区相对） |
| 阈值 | 默认 **0.7**；参数名 **`threshold`** |
| 多图 | 非重叠抑制（旧 find_all 风格） |
| 截帧 | 每次 find **当场** `capture.grab` |
| 找色 | `(R,G,B)` / `"#RRGGBB"` + tolerance + region + multi；失败 **`None`**（multi 为 `[]`） |
| 缺文件 | 抛 **`FileNotFoundError`** |

## 用户场景（摘要）

1. **找单图**：相对 resource_dir 路径；可选 region；成功返回 Match 中心，失败 `None`；缺文件抛错；每次新截帧。  
2. **找多图**：阈值以上非重叠匹配列表，无则 `[]`。  
3. **找色**：同上区域规则；单点 `None` / 多点列表。

边界：模板大于区域不崩溃；非法 region/颜色明确报错；截屏失败不得静默当未找到；Windows 非 ASCII 路径须能加载。

## 功能需求 / 成功标准

与英文版 FR-001–FR-012、SC-001–SC-005 信息等价。

## 假设与非范围

与英文版等价（OpenCV 类模板匹配、第一屏限制、旋转缩放增强不在范围；OCR/YOLO 见 `005-ocr-yolo-onnx` 等）。
