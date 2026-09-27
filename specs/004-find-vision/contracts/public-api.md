# Contract: Find Public API

**Feature**: `004-find-vision`

Chinese companion: [`public-api.zh-CN.md`](./public-api.zh-CN.md).

```text
engine.find.find_image(path, *, threshold=0.7, region=None) -> Match | None
engine.find.find_images(path, *, threshold=0.7, region=None) -> list[Match]
engine.find.find_color(color, *, tolerance=10, region=None, multi=False) -> ColorMatch | None | list[ColorMatch]
```

- `path`: relative to `resource_dir` (or absolute)
- `region`: `(x1,y1,x2,y2)` optional
- Missing template: `FileNotFoundError`
- Invalid region/color: `FindError` / `ValueError`
