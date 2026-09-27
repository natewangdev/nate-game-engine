"""Annotate BGR frames and save JPEG (CJK-capable)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

_FONT_CANDIDATES = (
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arial.ttf",
)


def _load_font(size: int = 22):
    from PIL import ImageFont

    for candidate in _FONT_CANDIDATES:
        path = Path(candidate)
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def annotate_and_save_jpeg(frame_bgr: np.ndarray, caption: str, path: Path) -> None:
    from PIL import Image, ImageDraw

    arr = np.asarray(frame_bgr)
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError("frame must be HxWx3 BGR")
    rgb = arr[:, :, :3][:, :, ::-1].copy()
    image = Image.fromarray(rgb)
    draw = ImageDraw.Draw(image)
    font = _load_font()
    xy = (8, 8)
    # Black outline then white fill (Pillow stroke).
    draw.text(
        xy,
        caption,
        font=font,
        fill=(255, 255, 255),
        stroke_width=2,
        stroke_fill=(0, 0, 0),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="JPEG", quality=90)
