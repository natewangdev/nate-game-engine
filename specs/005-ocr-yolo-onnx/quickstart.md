# Quickstart: OCR / YOLO

```powershell
uv sync --extra dev
uv run pytest -q
# YOLO ONNX under resource_dir/models/; OCR uses RapidOCR defaults
uv run python examples/yolo_smoke.py
uv run python examples/ocr_smoke.py
```
