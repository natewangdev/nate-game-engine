# 功能规格：视觉限时轮询 — OCR find_text、find_image 超时、YOLO detect 超时

**功能分支**：`007-vision-wait`

**创建**：2026-10-01

**状态**：草稿

**输入**：OCR 指定区域找特定文字（单/多结果 + 最大找字时间）；find 找图最大时间；YOLO detect 最大时间与间隔。

英文权威版：[`spec.md`](./spec.md)。

**扩展**：`004-find-vision`（`find_image`）、`005-ocr-yolo-onnx`（`recognize` / `detect`）。既有单次 API 保留；本功能新增 `find_text` 与可选限时轮询参数。落地后，这些 API 的等待/轮询行为以本文为准。

## 澄清（已锁定）

### Session 2026-10-01

| 主题 | 决策 |
|------|------|
| OCR API | **B**：新方法 `find_text`；不区分大小写子串；`recognize` 不变 |
| OCR 返回 | **A**：`OcrLine`；`multi=False` → `OcrLine \| None`；`multi=True` → `list[OcrLine]` |
| Find 范围 | **A**：仅 `find_image` 增加限时参数 |
| YOLO 超时返回 | **C**：始终 `list[Detection]`；超时/未检出 → `[]`（不用 `None`） |
| 时间语义 | **A**：`timeout_ms` / `interval_ms`；墙钟（含截屏+推理）；`timeout_ms > 0` 且 `< interval_ms` → `FindError`；`timeout_ms == 0` → 只一次 |

## 用户场景与测试

### 用户故事 1 - 区域内找特定文字（P1）

调用 `engine.ocr.find_text("组队", region=...)`；默认首个 `OcrLine` 或 `None`；`multi=True` 返回全部；可选 `timeout_ms` 轮询。

**验收**：子串匹配、单/多、`timeout_ms=0` 未找到、限时内早退、超时 `None`/`[]`、非法超时关系 → `FindError`。

### 用户故事 2 - 限时 find_image（P1）

`find_image` 增加 `timeout_ms`（默认 0）/ `interval_ms`（默认 500）；超时未找到 → `None`。

### 用户故事 3 - 限时 YOLO detect（P2）

`detect` 增加同样限时参数；一直检测到非空过滤结果或超时；超时仍 → `[]`。

### 边界情况

与英文版等价（空白查询、每轮 fresh grab、墙钟预算、关闭后 `ClosedError` 等）。

## 功能需求

- **FR-001**：`find_text`；子串 casefold；`recognize` 不变。
- **FR-002**：`multi` 控制 `OcrLine | None` vs `list[OcrLine]`。
- **FR-003**：`find_image` 的 `timeout_ms` / `interval_ms`；超时 → `None`。
- **FR-004**：`detect` 的 `timeout_ms` / `interval_ms`；超时 → `[]`。
- **FR-005**：非法 `timeout_ms < interval_ms` → `FindError`；`timeout_ms==0` 不 sleep。
- **FR-006**：墙钟毫秒；每轮 fresh grab。
- **FR-007**：坐标/region 与既有 move 对齐约定一致。
- **FR-008**：假对象自动化覆盖主路径与否定路径。

## 成功标准

与英文版 SC-001–SC-005 信息等价。

## 假设

默认间隔：OCR `1000`；find_image / detect `500`。参数名 `timeout_ms` / `interval_ms`。

## 非范围

不对 `find_images` / `find_color` / `recognize` 做限时；YOLO 不改为返回 `None`；无正则/纯精确匹配模式；无异步 API。
