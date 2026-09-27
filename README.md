# Nate Game Engine

English | [中文](README.zh-CN.md)

Python package for game scripting (**import name**: `nge2`).

PyPI name: `nate-game-engine`.

## Features (MVP)

- Instance API: `engine = nge2.NGE2(...)`
- Screen capture (`dxcam` / `mss`)
- Hardware HID control via ESP32-S3
- Window client-area coordinates (DPI-aware)
- Logging under root name `nge`
- Find image / find color (`engine.find`)
- OCR (RapidOCR) / YOLO (onnxruntime) — `engine.ocr`, `engine.yolo`
- Stubs removed for find/ocr/yolo capability APIs (instance facades)

Managed with Spec Kit — see `specs/001-nge2-mvp/`.

## Prerequisites

- Windows, Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- ESP32-S3 with compatible HID firmware (for real control)

## Quick start

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

### Hardware smoke (mouse move)

Requires ESP32-S3. See `examples/README.md`.

Edit constants in `examples/move_smoke.py`, then:

```powershell
uv run python examples/move_smoke.py
```

Validation details: `specs/001-nge2-mvp/quickstart.md`.

## Use from another project (local development)

While developing this engine locally, point your game-script (or other) project at
this repo with an **editable** install. Changes under `src/nge2/` are picked up
without reinstalling.

From the **consumer** project directory (adjust the path to your clone):

```powershell
# Recommended (uv)
uv add --editable D:\GitHub\nate-game-engine

# Or with pip
pip install -e D:\GitHub\nate-game-engine
```

Then in that project:

```python
import nge2

with nge2.NGE2(resource_dir=".", capture="dxcam") as engine:
    ...
```

Notes:

- Consumer needs Windows + Python 3.11+; real HID still needs ESP32-S3.
- Prefer an absolute path (or a stable relative path) to this repo.
- For a fixed released version (not live editing), use a git tag instead — see
  [Install from a tagged release](#install-from-a-tagged-release).

## Release (GitHub Actions)

GitHub Packages **does not** host Python/PyPI packages. This repo uses **tag-driven
releases** (approach B): the git tag is the source of truth for the version.

```powershell
# After merge to main (or on the commit you want to ship):
git tag v0.1.1
git push origin v0.1.1
```

Workflow `.github/workflows/publish.yml` will:

1. Strip the `v` prefix → `0.1.1`
2. Inject that into `pyproject.toml` (`uv version`)
3. `uv build`
4. Create a GitHub Release and attach `dist/*`

`pyproject.toml` / local `version` can stay at a placeholder; **published** builds
always take the tag. Do not re-use a tag that already has a Release.

### Install from a tagged release

```powershell
# Prefer: install from the git tag (source)
uv add "nate-game-engine @ git+https://github.com/natewangdev/nate-game-engine@v0.1.1"

# Or: download the `.whl` from the Release assets page / URL
```

For a public index (`pip install nate-game-engine`), publish to [PyPI](https://pypi.org/)
separately; the same tag → inject → build flow still applies.

## License

MIT
