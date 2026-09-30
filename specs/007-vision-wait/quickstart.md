# Quickstart: Vision wait/poll

Chinese companion: [`quickstart.zh-CN.md`](./quickstart.zh-CN.md).

## Unit (CI)

```powershell
uv run pytest tests/unit/test_vision_wait.py tests/unit/test_find.py tests/unit/test_ocr_yolo.py -q
```

## Hardware smokes

```powershell
uv run python examples/find_text_smoke.py
uv run python examples/find_wait_smoke.py
uv run python examples/yolo_wait_smoke.py
```

Edit `TIMEOUT_MS` / `INTERVAL_MS` (and `TEXT` / template region / model paths) at the top of each script.
See [contracts/public-api.md](./contracts/public-api.md).
