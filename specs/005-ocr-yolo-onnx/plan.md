# Implementation Plan: OCR (RapidOCR) + YOLO (ONNX Runtime)

**Branch**: `005-ocr-yolo-onnx` | **Date**: 2026-09-27 | **Spec**: [spec.md](./spec.md)

Chinese companion: [`plan.zh-CN.md`](./plan.zh-CN.md).

## Summary

Per-instance facades loaded at `NGE2` construct: **OCR = RapidOCR** (legacy nge style; default models via RapidOCR), **YOLO = CPU onnxruntime** (explicit model path). Shared `_vision` crop/coords with `find`. Tests use factories. Amend OCR implementation away from hand-rolled det+rec.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `rapidocr-onnxruntime` (or plan-chosen RapidOCR package) + `onnxruntime` (CPU); `numpy`, `opencv-python-headless`  
**Testing**: pytest + FakeCapture + FakeOcr/FakeYolo factories  
**Target Platform**: Windows  
**Project Type**: Library incremental  

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I–III | PASS | Facades + fakes |
| IV | PASS | RapidOCR + onnxruntime justified; YOLO weights not packaged |
| V–VII | PASS | Additive; bilingual |

## Project Structure

```text
src/nge2/ocr/__init__.py     # RapidOCR-backed Ocr, OcrLine
src/nge2/yolo/__init__.py    # ORT Yolo, Detection
src/nge2/_engine.py          # construct-time load; ocr_kwargs; yolo paths
```

## Complexity Tracking

None.
