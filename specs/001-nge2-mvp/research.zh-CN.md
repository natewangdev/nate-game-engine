# 研究记录：nge2 MVP 核心引擎

**功能**：`001-nge2-mvp` | **日期**：2026-09-26

> 英文权威版：[`research.md`](./research.md)。执行 Spec Kit 时忽略本中文版。

## 1. 包布局与入口 API

- **决策**：import 包 `nge2`；主类型 `NGE2`，含 `close()` 与上下文管理器；经 `engine.capture` 等访问。
- **理由**：对齐已确认规格与宪章库优先。
- **备选**：模块级 `init` 单例 — 已否决。

## 2. 截屏后端

- **决策**：严格使用构造所选后端；不可用则构造失败；不回退。`release` 后 `grab` 重建同一后端。仅第一块显示器；BGR `ndarray`；区域为屏幕物理像素。
- **理由**：澄清结论 + 旧工具经验。
- **备选**：自动回退、进程全局 capture — 已否决。

## 3. HID 传输与键位

- **决策**：移植既有串口行协议与 keymap Usage ID 表到 `control/_transport.py`、`control/_keymap.py`。绝对移动 `MA`；完整点击 `CLK`；左右键按下/抬起 `BTN`（对应 `left_down`/`left_up`/`right_down`/`right_up`）；键盘 `KD`/`KU`/`KP`/`MOD`；关闭时 `STOP`（须释放按住的键鼠）。
- **理由**：固件已存在；规格要求 keymap 等价与 `BTN` 公开 API。
- **备选**：改协议 / 相对鼠标 — 超出范围或破坏兼容。

## 4. 拟人 / geom

- **决策**：内部 `geom`（贝塞尔类路径）；仅 `humanize=True` 使用；`False` 时瞬时移动并忽略 duration/spread。
- **理由**：FR-009/013。
- **备选**：对外稳定 geom API — MVP 不做。

## 5. 窗口与 DPI

- **决策**：构造时声明 DPI aware；`GetClientRect` + `ClientToScreen`；`window` 暴露 hwnd/标题/客户区。
- **理由**：FR-004/010/011。
- **备选**：依赖调用方自行设 DPI — 易错。

## 6. 日志

- **决策**：根名 `nge`；控制台 + 文件（默认 cwd `nge.log`）；`NGE_LOG_LEVEL`。
- **理由**：FR-012 与产品方选择。
- **备选**：根名 `nge2` — 已否决。

## 7. 空壳与延后视觉

- **决策**：`find`/`ocr`/`yolo` 可 import，能力调用抛 `NotImplementedError`；MVP 不引入 RapidOCR/YOLO 依赖。
- **理由**：澄清 A + 全量安装针对受支持 MVP 模块。
- **备选**：省略模块 — 与八模块包面冲突。

## 8. 依赖集

- **决策**：`numpy`、`dxcam`、`mss`、`pyserial`（及 dxcam 所需传递依赖）。
- **理由**：宪章 IV。
- **备选**：extras — 已被 v1.2.0 取代。

## 9. 测试策略

- **决策**：keymap/geom/坐标/空壳/构造校验单测；假 transport/grabber；真机可选标记。
- **理由**：FR-017、宪章 II/III。

## 10. 端口互斥

- **决策**：进程级跟踪已打开端口；第二实例争用同一设备则构造失败。
- **理由**：澄清 Q5。
