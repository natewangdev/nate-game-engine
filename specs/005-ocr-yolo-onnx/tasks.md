# Tasks: OCR RapidOCR + YOLO ORT

Chinese companion: [`tasks.zh-CN.md`](./tasks.zh-CN.md).

- [x] T001–T009 Prior ORT-OCR + YOLO work (superseded for OCR backend)
- [x] T010 Update deps: add RapidOCR package; drop OCR reliance on caller det/rec paths
- [x] T011 Rework `src/nge2/ocr/` to RapidOCR engine created at construct; map results to `OcrLine`
- [x] T012 Update `NGE2` ctor: remove primary `ocr_det`/`ocr_rec`/`ocr_keys`; add `ocr_kwargs`; keep eager OCR+YOLO load
- [x] T013 Update fakes/tests/examples/README for RapidOCR defaults
- [x] T014 `uv run pytest -q` green; mark tasks done
