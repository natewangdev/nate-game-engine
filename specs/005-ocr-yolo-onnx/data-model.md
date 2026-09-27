# Data Model: OCR / YOLO

**Feature**: `005-ocr-yolo-onnx`

Chinese companion: [`data-model.zh-CN.md`](./data-model.zh-CN.md).

## OcrLine

| Field | Type | Notes |
|-------|------|-------|
| text | str | From RapidOCR |
| score | float | |
| x, y | int | Move-aligned center |
| box | tuple[int,int,int,int] | `(x1,y1,x2,y2)` move-aligned |

## Detection

| Field | Type | Notes |
|-------|------|-------|
| x, y | int | Move-aligned center |
| width, height | int | |
| score | float | |
| class_id | int | |
| label | str | From names or `str(class_id)` |

## Runtimes

- **Ocr**: one RapidOCR engine per `NGE2`
- **Yolo**: one ORT InferenceSession + optional names list per `NGE2`
