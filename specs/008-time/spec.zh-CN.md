# 功能规格：Time 模块 — sleep / delay（固定与随机毫秒延时）

**功能分支**：`008-time`

**创建**：2026-10-01

**状态**：草稿

**输入**：增加 time 模块；delay 支持单参固定延时与双参（最小、最大）随机延时，单位毫秒；可通过 `engine.time…` 与静态/import 调用；并请建议游戏脚本侧其它时间方法。

英文权威版：[`spec.md`](./spec.md)。

**新领域**：新增包领域 `time`（与 `capture` / `control` / `ocr` / `yolo` / `find` / `log` / `geom` / `window` 并列）。无硬件 / COM / 桌面依赖。落地后，公开 sleep/delay 行为以本文为准。

## 澄清（已锁定）

### Session 2026-10-01

| 主题 | 决策 |
|------|------|
| API 命名与签名 | **B**：主名 **`sleep`**；一参 = 固定 ms；两参 `(min_ms, max_ms)` = 随机 ms；可选 **`delay`** 别名，行为完全相同 |
| 本功能范围 | **B**：仅 `sleep`（+ `delay` 别名）；其它时间工具一律延后 |
| 随机与调用面 | **C**：均匀闭区间 `[min_ms, max_ms]`；`min > max` 或负值 → 明确报错；`from nge2.time import sleep` / `Time.sleep` / `engine.time.sleep` 三者等价；无实例状态 |
| 返回值与错误 | **A**：成功返回实际延时 **`int` ms**；非法参数 → **`ValueError`**（不新增 `TimeError`） |

- Q: 延时命名与固定/随机签名？ → A: **B**
- Q: 本功能纳入哪些时间工具？ → A: **B**（仅 sleep + delay）
- Q: 随机分布与调用面？ → A: **C**
- Q: 返回值与异常类型？ → A: **A**

## 用户场景与测试

### 用户故事 1 - 固定毫秒延时（P1）

脚本作者用 `engine.time.sleep(500)` 或 `from nge2.time import sleep; sleep(500)` 在动作间停顿；调用返回实际延时 `500`。

**验收**：合法非负整数延时；`sleep(0)` 立即返回 `0`；`delay` 与 `sleep` 行为一致。

### 用户故事 2 - 闭区间随机延时（P1）

`engine.time.sleep(200, 800)` 在 `[min_ms, max_ms]` 上均匀抽样并睡眠；返回实际抽样毫秒以便日志/断言。

**验收**：`min <= d <= max`；`min == max` 等同固定延时；闭区间端点可达。

### 用户故事 3 - 三种调用面等价（P1）

`engine.time.sleep`、`Time.sleep`、模块 import 的 `sleep`（及对应 `delay`）语义一致、无隐藏 per-engine 状态。

**验收**：相同合法参数返回等价；相同非法参数均抛 `ValueError`；多引擎实例行为不依赖可变时间状态。

### 边界情况

与英文版等价（负值、`min > max`、非整数、超大合法整数、中断、关闭引擎仍可用 import/`Time` 等）。

## 功能需求

- **FR-001**：提供 `sleep`；一参固定；两参闭区间均匀随机（整数 ms）。
- **FR-002**：提供 `delay` 作为 `sleep` 的别名。
- **FR-003**：时长须为非负整数 ms；非法 → `ValueError`（睡眠前）。
- **FR-004**：成功返回实际延时 `int`。
- **FR-005**：模块函数 / `Time` / `engine.time` 三者等价；无实例时间状态。
- **FR-006**：本功能公开面仅限 `sleep` 与 `delay`；其它建议工具不在范围。
- **FR-007**：自动化测试覆盖固定/随机/别名/三调用面/非法参数；无需真实桌面硬件。

## 成功标准

与英文版 SC-001–SC-005 信息等价。

## 假设

单位为整数毫秒，与既有 `timeout_ms` 约定一致；`delay` 为可选别名；本功能不做高斯/拟人分布；规划/实现时同步更新 constitution 领域列表中的 `time`。

## 非范围

`monotonic_ms` / `now_ms` / `Stopwatch` / `wait_until` / 墙钟定时；不改造 `control`/`geom`/视觉轮询内部 sleep；无异步 sleep；不保证亚毫秒定时精度。
