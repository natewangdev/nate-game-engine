# Nate Game Engine

[English](README.md) | 中文

用于游戏脚本的 Python 包（**导入名**：`nge2`）。

PyPI 包名：`nate-game-engine`。

## 功能（MVP）

- 实例 API：`engine = nge2.NGE2(...)`
- 屏幕截取（`dxcam` / `mss`）
- 通过 ESP32-S3 的硬件 HID 控制
- 窗口客户区坐标（DPI 感知）
- 日志根名为 `nge`
- 找图 / 找色（`engine.find`）
- OCR（RapidOCR）/ YOLO（onnxruntime）— `engine.ocr`、`engine.yolo`
- find / ocr / yolo 能力 API 已去掉 stub（实例门面）

由 Spec Kit 管理 — 见 `specs/001-nge2-mvp/`。

## 前置条件

- Windows，Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- 刷好兼容固件的 ESP32-S3（真实控制时需要）

## 快速开始

```powershell
uv sync --extra dev
uv run pytest -q
```

```python
import nge2

with nge2.NGE2(resource_dir=".", capture="dxcam") as engine:
    frame = engine.capture.grab()
    engine.control.move(100, 100)
    engine.control.left_click()
```

### 硬件冒烟（鼠标移动）

需要 ESP32-S3。详见 `examples/README.md`。

编辑 `examples/move_smoke.py` 顶部常量后执行：

```powershell
uv run python examples/move_smoke.py
```

验收细节：`specs/001-nge2-mvp/quickstart.md`。

## 本地开发：在其他项目中使用

在本地开发本引擎时，可在游戏脚本（或其他）项目里用 **可编辑（editable）安装**
指向本仓库。修改 `src/nge2/` 后无需重新安装即可生效。

在**消费方**项目目录执行（路径改成你的本机克隆位置）：

```powershell
# 推荐（uv）
uv add --editable D:\GitHub\nate-game-engine

# 或使用 pip
pip install -e D:\GitHub\nate-game-engine
```

然后在该项目中：

```python
import nge2

with nge2.NGE2(resource_dir=".", capture="dxcam") as engine:
    ...
```

说明：

- 消费方需 Windows + Python 3.11+；真实 HID 仍需要 ESP32-S3。
- 路径建议用绝对路径（或稳定的相对路径）指向本仓库。
- 若要固定已发布版本（而非边改边用），请改用 git tag 安装 — 见
  [从带 tag 的发版安装](#从带-tag-的发版安装)。

## 发版（GitHub Actions）

GitHub Packages **不提供** Python/PyPI 仓库。本仓库采用 **tag 驱动发版**（方式 B）：
**git tag 即为版本号的唯一来源**。

```powershell
# 合并到 main（或选定要发布的 commit）之后：
git tag v0.1.1
git push origin v0.1.1
```

工作流 `.github/workflows/publish.yml` 会：

1. 去掉 `v` 前缀 → `0.1.1`
2. 写入 `pyproject.toml`（`uv version`）
3. 执行 `uv build`
4. 创建 GitHub Release，并挂上 `dist/*`

本地 `pyproject.toml` 的 `version` 可保持占位；**正式构建产物**一律以 tag 为准。
已发布过的 tag / Release 不要复用。

### 从带 tag 的发版安装

```powershell
# 推荐：按 git tag 安装（源码）
uv add "nate-game-engine @ git+https://github.com/natewangdev/nate-game-engine@v0.1.1"

# 或：从 Release 资源页 / URL 下载 `.whl`
```

若需要公共索引（`pip install nate-game-engine`），请另行发布到 [PyPI](https://pypi.org/)；
同样适用「tag → 注入版本 → 构建」流程。

## 许可证

MIT
