# Research: Find Vision

**Feature**: `004-find-vision`

Chinese companion: [`research.zh-CN.md`](./research.zh-CN.md).

## 1. Engine-bound Find object

- **Decision**: `self.find = Find(engine)` with methods; not free module functions needing engine args.
- **Rationale**: Spec `engine.find.find_image`; needs resource_dir/capture/window.

## 2. OpenCV headless

- **Decision**: Depend on `opencv-python-headless` (not full GUI opencv).
- **Rationale**: matchTemplate + imdecode; smaller; CI-friendly.

## 3. Grab strategy

- **Decision**: Always full primary grab then numpy-crop to search rect in screen space (same as ERROR screenshot fix); avoids region-backend quirks.
- **Rationale**: Consistent with dxcam numpy processor.

## 4. Color search

- **Decision**: BGR frame vs RGB input converted; per-channel abs diff ≤ tolerance; single = first match in row-major scan (or centroid of blob — use first pixel for simplicity); multi capped at 500.
- **Rationale**: Spec miss→None; predictable.
