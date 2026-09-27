# Research: OCR RapidOCR + YOLO ORT

**Feature**: `005-ocr-yolo-onnx`

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. YOLO runtime

- **Decision**: `onnxruntime` CPUExecutionProvider; Ultralytics YOLOv8-detect style postprocess.
- **Rationale**: Spec locked CPU ORT for YOLO.

## 2. OCR runtime (amended)

- **Decision**: Use **RapidOCR** (`rapidocr-onnxruntime`, same family as legacy `nge.ocr.OCREngine`) created **eagerly in `NGE2.__init__`**.
- **Rationale**: User amendment — match legacy quality/ergonomics; avoid maintaining a simplified det+rec pipeline that underperforms RapidOCR defaults.
- **Alternatives rejected**: Hand-rolled PP-OCR det+rec ORT as public OCR backend.

## 3. Construct-time load

- **Decision**: Both OCR (RapidOCR instance) and YOLO (InferenceSession) created during `NGE2` construction; failures → `ConstructError`.
- **Rationale**: Spec load timing locked; user wants OCR aligned with YOLO eagerness.

## 4. Model supply

- **Decision**: YOLO requires caller ONNX path. OCR uses RapidOCR default models (package/download); optional `ocr_kwargs` for overrides.
- **Rationale**: Matches legacy OCR UX; YOLO remains explicit.

## 5. Test isolation

- **Decision**: `ocr_factory` / `yolo_factory` on `NGE2` for CI fakes (no network download / no YOLO weights).
- **Rationale**: FR-011.

## 6. Shared vision crop

- **Decision**: Keep `_vision` helpers for region/crop/move coords shared with find.
- **Rationale**: FR-009.

## 7. Close / release

- **Decision**: `Ocr.close()` / `Yolo.close()` drop engine/session refs; `NGE2.close()` calls both; post-close → `ClosedError`.
- **Rationale**: FR-016.
