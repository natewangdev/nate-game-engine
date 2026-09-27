# Contract: OCR / YOLO Public API

**Feature**: `005-ocr-yolo-onnx`

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

```text
NGE2(
  ...,
  yolo_model="models/yolo.onnx",
  yolo_names="models/yolo.names",
  ocr_kwargs=None,        # optional RapidOCR kwargs
  ocr_factory=None,       # test hook
  yolo_factory=None,      # test hook
)

engine.ocr.recognize(*, region=None) -> list[OcrLine]
engine.yolo.detect(*, conf=0.25, iou=0.45, region=None, class_ids=None) -> list[Detection]
```

Errors: missing YOLO / RapidOCR init failure → `ConstructError`; invalid region → `FindError`; undersized crop → `[]`.
`NGE2.close()` releases OCR/YOLO; post-close `recognize`/`detect` → `ClosedError`.

Removed as primary API: `ocr_det`, `ocr_rec`, `ocr_keys`.
