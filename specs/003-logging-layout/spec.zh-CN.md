# 功能规格：按日文件日志与 ERROR 截图

**功能分支**：`003-logging-layout`

**创建**：2026-09-27

**状态**：草稿

**输入**：`log_dir` 构造参数（默认 cwd/logs）；按日目录与前导零序号日志文件；`logger.error` 时窗口/全屏 JPG 叠字；控制台与文件均不含模块名；移除 `enable_file_logging`。

> 英文权威版：[`spec.md`](./spec.md)。执行 Spec Kit 时忽略本中文版。

**部分取代**：`001-nge2-mvp` 中关于 cwd 下默认 `nge.log` 与可选 `enable_file_logging` 的约定；本功能生效后以本规格的 `log_dir` 与目录布局为准。

## 已锁定澄清

| 主题 | 决定 |
|------|------|
| 当日序号 | 扫描当日 `nge-*.log`，max+1；**3 位前导零**（`nge-001.log`） |
| 跨午夜 | **A**：整次运行固定使用构造当日目录 |
| 多实例 | **A**：每实例独立日志文件并各自占序号 |
| 截图触发 | **仅** `logging.ERROR` / `logger.error(...)` |
| 截图格式 | JPEG（`.jpg`） |
| 截图文件名 | `{log_dir}/{YYYY-MM-DD}/screenshot/{HHMMSS}-{xxx}.jpg`，`{xxx}` 为当日截图 3 位序号 |
| 叠字 | 白字 + 黑描边；中文清晰 |
| 截图失败 | 只打日志，不阻断业务 |
| 格式 | 控制台与文件均**不含** logger 名 |
| `enable_file_logging` | **删除**；构造成功即写文件日志 |

## 用户场景与测试 *(必填)*

### 用户故事 1 - 配置日志目录与按日文件（优先级：P1）

作者传入 `log_dir` 或省略（默认 `{cwd}/logs`）。构造时创建 `{log_dir}/{YYYY-MM-DD}/` 并打开新的 `nge-{NNN}.log`。控制台与文件行均不含模块名。

**验收要点**：默认目录、显式目录、序号递增、跨午夜不切换、多实例多文件、无 `nge.capture` 名。

---

### 用户故事 2 - ERROR 时带说明的截图（优先级：P1）

`logger.error` 时截取绑定窗口客户区（有 hwnd）或第一屏全屏；左上角叠本地时间与错误文案（白字黑边、中文清晰）；存入当日 `screenshot` 下 JPG。失败只记日志。

**验收要点**：有/无 hwnd、失败软降级、INFO/WARNING 不截图。

---

### 边界情况

- 相对 `log_dir` 相对构造时 cwd 解析。
- 日期用本地时区 `YYYY-MM-DD`。
- 序号默认 3 位；超过 999 时加宽位数且不失败。
- 截图 `{xxx}` 与日志文件序号相互独立。
- 超长错误文案截断叠字（如 200 字 + 省略号）。
- 引擎已关闭 / capture 已 release：截图软失败。
- 不再接受 `enable_file_logging`。

## 功能需求

与英文版 FR-001–FR-012 信息等价：`log_dir`、按日 `nge-NNN.log`、构造日固定、多实例独立文件、无模块名、`NGE_LOG_LEVEL`、仅 ERROR 截 JPG、叠字与软失败、移除 `enable_file_logging`、CI mock 覆盖。

## 成功标准

与英文版 SC-001–SC-005 信息等价。

## 假设与非范围

与英文版 Assumptions / Out of Scope 信息等价（本地时区、字体回退、无按大小轮转、无午夜切换、无 excepthook 等）。
