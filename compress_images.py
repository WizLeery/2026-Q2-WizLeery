#!/usr/bin/env python3
"""Compress portfolio images in place for web upload."""
import os
from pathlib import Path
from PIL import Image

IMG_DIR = Path("images")
MAX_SIDE = 1920
JPG_QUALITY = 85

files = sorted([f for f in IMG_DIR.iterdir() if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif")])
print(f"Compressing {len(files)} images...\n")

for src in files:
    try:
        img = Image.open(src)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > MAX_SIDE:
            ratio = MAX_SIDE / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        img.save(src, "JPEG", quality=JPG_QUALITY, optimize=True)
        print(f"{src.name} ({src.stat().st_size // 1024}KB)")
    except Exception as e:
        print(f"FAILED {src.name}: {e}")

print("\nDone.")
