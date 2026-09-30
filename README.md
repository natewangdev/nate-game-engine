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
- For a fixed released version (not live editing), install from PyPI or a git tag — see
  [Install a released version](#install-a-released-version).

## Release (GitHub Actions)

This repo uses **tag-driven releases**: the git tag is the source of truth for the
version. Pushing a `v*` tag builds the package, creates a GitHub Release, and
publishes to [PyPI](https://pypi.org/) via OIDC Trusted Publisher (`environment: pypi`).

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
5. Publish to PyPI (`pypa/gh-action-pypi-publish`, no API token)

`pyproject.toml` / local `version` can stay at a placeholder; **published** builds
always take the tag. Do not re-use a tag / version that already exists on PyPI or
as a GitHub Release.

### Install a released version

```powershell
# Prefer: public index
uv add nate-game-engine
# pip install nate-game-engine

# Alternatives: git tag, or download the `.whl` from the Release assets
uv add "nate-game-engine @ git+https://github.com/natewangdev/nate-game-engine@v0.1.1"
```

## License

MIT
