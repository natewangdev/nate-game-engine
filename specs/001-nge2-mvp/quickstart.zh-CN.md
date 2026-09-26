# 快速验证指南：nge2 MVP 核心引擎

**功能**：`001-nge2-mvp` | **日期**：2026-09-26

> 英文权威版：[`quickstart.md`](./quickstart.md)。执行 Spec Kit 时忽略本中文版。

## 前置

- Windows、Python 3.11+
- 兼容固件的 ESP32-S3（真机路径）
- 可写的 `resource_dir`（MVP 可为空目录）

## 安装

```powershell
cd <repo-root>
uv sync --extra dev
```

## 自动化（无硬件）

```powershell
uv run pytest -q
```

**期望**：默认测试全部通过（mock 串口/截屏）。

## 手工真机

使用 `with nge2.NGE2(resource_dir=".", ...) as engine:` 执行 grab → move → left_click → key_click；退出 `with` 后串口应释放，第二实例可再次获取设备。

负面：无设备构造失败；端口忙时第二实例失败；`control_mode=0/1` 构造失败。

## 完成标准

- [ ] CI 上 `uv run pytest` 通过
- [ ] 真机最小脚本成功
- [ ] 端口忙与 mode 0/1 失败符合规格
