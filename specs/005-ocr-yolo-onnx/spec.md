# Feature Specification: OCR (RapidOCR) and YOLO (ONNX Runtime)

**Feature Branch**: `005-ocr-yolo-onnx`

**Created**: 2026-09-27

**Status**: Draft

**Input**: User description: "Add YOLO and OCR modules; each unique per NGE2 instance. OCR uses RapidOCR (legacy nge style); YOLO uses onnxruntime. Both loaded at NGE2 construction."

Chinese companion (human-readable only): [`spec.zh-CN.md`](./spec.zh-CN.md).

**Supersedes (partial)**: `001-nge2-mvp` FR-015 (OCR/YOLO stubs only). After this feature, OCR recognition and YOLO detection behavior defined here is authoritative.

## Clarifications (locked)

### Session 2026-09-27

| Topic | Decision |
|-------|----------|
| Model load timing | **A**: Load OCR + YOLO during `NGE2` construction; failure → `ConstructError` |
| YOLO backend | **A**: CPU `onnxruntime` only; no CUDA EP in this feature |
| YOLO model path | Constructor params with overridable defaults under `resource_dir`; YOLO model required |
| Frame / coords | **A**: Same rules as `find` / `move` — fresh `capture.grab` each call; optional `region`; move-aligned return coords |
| Invalid region | **`FindError`** |
| Result order | **`score` descending** (stable ties) |
| OCR `box` | Required axis-aligned `box` + center `x,y` |
| Undersized crop | Return `[]` |
| Close | `NGE2.close()` releases OCR + YOLO; post-close → `ClosedError` |

### Session 2026-09-27 (OCR backend amendment)

| Topic | Decision |
|-------|----------|
| OCR stack | **RapidOCR** (same approach as legacy `nate-gaming-engine` / `rapidocr_onnxruntime`), **not** a hand-rolled det+rec ORT pipeline |
| OCR load timing | Still **eager at `NGE2` construct** (aligned with YOLO) — create the RapidOCR engine once per instance |
| OCR model paths | **Not required** for default use; RapidOCR supplies / downloads its default PP-OCR models. Optional RapidOCR kwargs MAY override models/thresholds |
| Removed | Constructor requirement for `ocr_det` / `ocr_rec` / `ocr_keys` as the primary OCR API |

- Q: Switch OCR from raw onnxruntime det+rec to RapidOCR while keeping construct-time load? → A: **Yes** — RapidOCR at construct; YOLO unchanged (ORT + explicit model path).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Construct with OCR + YOLO (Priority: P1)

A script author constructs `NGE2(resource_dir=..., yolo_model=...)`. The engine creates exactly one **RapidOCR** runtime and one **YOLO** onnxruntime session for that instance. Construction fails with `ConstructError` if RapidOCR cannot be initialized or the YOLO model cannot be loaded.

**Why this priority**: Eager load + per-instance uniqueness is the foundation for all recognition/detection calls.

**Independent Test**: Missing YOLO path → `ConstructError`; OCR factory / YOLO factory for CI; successful construct exposes `engine.ocr` / `engine.yolo` facades.

**Acceptance Scenarios**:

1. **Given** a valid YOLO ONNX path and RapidOCR available, **When** `NGE2` is constructed (no OCR model paths), **Then** construction succeeds and exposes `engine.ocr` and `engine.yolo`.
2. **Given** a missing `yolo_model` file, **When** `NGE2` is constructed, **Then** `ConstructError` is raised (capture cleanup rules unchanged).
3. **Given** RapidOCR import/init failure, **When** `NGE2` is constructed, **Then** `ConstructError` is raised.
4. **Given** two `NGE2` instances, **When** both are constructed, **Then** each owns its own OCR and YOLO runtimes (no shared mutable engines across instances).

---

### User Story 2 - YOLO detect (Priority: P1)

A script author calls `engine.yolo.detect(...)` to get object detections from a fresh screen grab (optional region). Results include move-aligned box centers/sizes, confidence, class id, and label when a names file is available.

**Why this priority**: Primary vision detection primitive for game scripting.

**Independent Test**: Injected YOLO runner + FakeCapture; assert Detection fields, coords, conf filter, score order.

**Acceptance Scenarios**:

1. **Given** a bound hwnd, **When** `detect` runs without region, **Then** search uses the full client area and returned centers are client-relative.
2. **Given** no hwnd, **When** `detect` runs without region, **Then** search uses the first-display frame and returned centers are screen absolute.
3. **Given** `region=(x1,y1,x2,y2)`, **When** `detect` runs, **Then** only that rectangle is searched (hwnd rules same as find).
4. **Given** detections below `conf`, **When** results return, **Then** those boxes are excluded.
5. **Given** two successive `detect` calls, **When** each runs, **Then** each performs its own fresh `capture.grab`.
6. **Given** multiple detections above `conf`, **When** `detect` returns, **Then** the list is ordered by `score` descending.

---

### User Story 3 - OCR recognize via RapidOCR (Priority: P1)

A script author calls `engine.ocr.recognize(...)` to read text lines from a fresh grab (optional region) using the instance RapidOCR engine created at construct. Each line includes text, score, move-aligned center, and required axis-aligned `box`.

**Why this priority**: Match legacy nge OCR quality/ergonomics while keeping nge2 instance API.

**Independent Test**: FakeOcr / injected RapidOCR double + FakeCapture; assert line fields and empty → `[]`.

**Acceptance Scenarios**:

1. **Given** text present in the search area, **When** `recognize` runs, **Then** returned lines use move-aligned coordinates, include required `box`, and non-empty `text` where recognized.
2. **Given** no readable text, **When** `recognize` runs, **Then** an empty list is returned (not an error).
3. **Given** optional `region`, **When** `recognize` runs, **Then** region/hwnd rules match find/YOLO.
4. **Given** two successive recognizes, **When** each runs, **Then** each triggers a fresh `capture.grab`.
5. **Given** multiple lines, **When** `recognize` returns, **Then** the list is ordered by `score` descending.

---

### Edge Cases

- Invalid/empty `region` → raise **`FindError`**.
- Missing/corrupt YOLO ONNX or RapidOCR init failure → `ConstructError` at construct.
- Capture failure during recognize/detect → propagate capture error (not empty success).
- YOLO with no `yolo_names` file → `label` may be empty/`str(class_id)`; detection still works.
- Undersized search crop → return **`[]`** (MAY debug-log).
- After `NGE2.close()`, OCR/YOLO MUST be released; further `recognize`/`detect` → **`ClosedError`**.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Public APIs MUST be instance facades `engine.ocr` and `engine.yolo`, one OCR runtime and one YOLO runtime per `NGE2` instance.
- **FR-002**: YOLO inference MUST use **onnxruntime** CPU Execution Provider only in this feature.
- **FR-002b**: OCR MUST use **RapidOCR** (onnxruntime-backed RapidOCR package, aligned with legacy nge). Hand-rolled det+rec ORT pipelines are out of scope for OCR.
- **FR-003**: `NGE2` construction MUST initialize the RapidOCR engine and load the YOLO session before returning a usable instance; failure → `ConstructError`.
- **FR-004**: YOLO model path MUST be a constructor parameter with overridable default relative to `resource_dir` (absolute allowed). Required: `yolo_model`. Optional: `yolo_names`. OCR MUST NOT require `ocr_det` / `ocr_rec` / `ocr_keys` for default operation.
- **FR-005**: Optional constructor `ocr_kwargs` (or equivalent) MAY be forwarded to RapidOCR for thresholds / custom model paths; defaults MUST work with no OCR path args.
- **FR-006**: `engine.yolo.detect(*, conf=0.25, iou=0.45, region=None, class_ids=None) -> list[Detection]` MUST return detections after confidence filter and NMS (`iou`); empty list if none; ordered by **`score` descending**.
- **FR-007**: `engine.ocr.recognize(*, region=None) -> list[OcrLine]` MUST return RapidOCR lines mapped to `OcrLine`; empty list if none; ordered by **`score` descending**; each line MUST include move-aligned `x`/`y` and **`box`**.
- **FR-008**: Each recognize/detect call MUST obtain a fresh frame via this engine’s `capture.grab` (full grab then crop as needed, consistent with find).
- **FR-009**: Optional `region` and returned coordinates MUST follow the same hwnd/client vs screen rules as `find` / `control.move`. Invalid/empty `region` MUST raise **`FindError`**.
- **FR-010**: Default install MUST include **RapidOCR** (onnxruntime backend) and **onnxruntime** (CPU) per constitution full-install rule; justify in plan. YOLO weights are NOT shipped; RapidOCR default weights follow RapidOCR’s own distribution/download behavior.
- **FR-011**: Automated tests MUST cover construct failure paths and recognize/detect with fakes (no mandatory large YOLO weights / no network model download required in CI).
- **FR-012**: Module-level stub `NotImplementedError` entrypoints for OCR/YOLO capability MUST be replaced by the instance facade behavior for these APIs.
- **FR-015**: If the search crop is smaller than a practical minimum, `detect` / `recognize` MUST return an empty list (not raise). Implementation MAY emit a debug log.
- **FR-016**: `NGE2.close()` MUST release this instance’s OCR and YOLO runtimes. Idempotent `close` MUST NOT raise. After close, `recognize` / `detect` MUST raise **`ClosedError`**.

### Key Entities

- **OcrLine**: `text` (str), `score` (float), `x`/`y` (int, move-aligned center), **`box=(x1,y1,x2,y2)`** (required, move-aligned).
- **Detection**: `x`/`y`, `width`/`height`, `score`, `class_id`, `label`.
- **Runtimes**: one RapidOCR engine + one YOLO InferenceSession per `NGE2` instance.

### Designed public surface (normative for this feature)

```text
NGE2(
  resource_dir,
  ...,
  yolo_model="models/yolo.onnx",
  yolo_names="models/yolo.names",  # optional
  ocr_kwargs=None,                 # optional dict forwarded to RapidOCR
)

engine.ocr.recognize(*, region=None) -> list[OcrLine]
engine.yolo.detect(*, conf=0.25, iou=0.45, region=None, class_ids=None) -> list[Detection]
engine.ocr.close() / engine.yolo.close()  # also invoked by NGE2.close()
```

RapidOCR internal model files and optional orientation classifier are implementation details of RapidOCR. Spec requires stable **Python** return types above.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authors can construct without OCR model paths (RapidOCR defaults) and with a local YOLO ONNX, then call `detect` / `recognize` with move-aligned coords when hwnd is set.
- **SC-002**: Missing YOLO model or RapidOCR init failure at construct fails with `ConstructError` (no successful instance).
- **SC-003**: CI tests pass with fakes (no YOLO weights / no OCR model download required).
- **SC-004**: Two engine instances do not share OCR/YOLO runtime objects.
- **SC-005**: Region/coord behavior for OCR/YOLO matches find acceptance rules in the same hwnd fixtures.
- **SC-006**: After `close()`, recognize/detect raises `ClosedError` in automated tests.

## Assumptions

- YOLO task is **object detection** for a single ONNX detect export (e.g. Ultralytics YOLOv8-style).
- RapidOCR package choice (`rapidocr-onnxruntime` vs `rapidocr` + `onnxruntime`) is fixed in plan/research to match legacy behavior as closely as practical.
- First-display-only capture limitation from MVP still applies when searching without hwnd.

## Out of Scope

- CUDA / TensorRT / DirectML as first-class nge2 providers (RapidOCR/ORT may use CPU only as configured)
- Hand-rolled PP-OCR det+rec ORT pipeline as the OCR public backend
- Training / fine-tuning / bundling YOLO weights inside the PyPI package
- Streaming / async inference APIs
- Changing find-image/find-color behavior
