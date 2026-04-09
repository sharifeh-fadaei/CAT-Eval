from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


class ImageNotFound(Exception):
    pass


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _first_image_in_dir(directory: Path) -> Optional[Path]:
    if not directory.exists() or not directory.is_dir():
        return None
    images = [f for f in directory.iterdir() if f.suffix.lower() in IMAGE_EXTS]
    if not images:
        return None
    return sorted(images, key=lambda p: len(p.name))[0]


def find_image(dataset_root: Path, sample_name: str) -> Path:
    dataset_root = Path(dataset_root)
    primary_dir = dataset_root / sample_name
    image = _first_image_in_dir(primary_dir)
    if image:
        return image

    # fallback search
    candidates = []
    for root, _, files in os.walk(dataset_root):
        for fname in files:
            path = Path(root) / fname
            if path.suffix.lower() not in IMAGE_EXTS:
                continue
            if sample_name in fname:
                candidates.append(path)
    if candidates:
        return sorted(candidates, key=lambda p: len(p.name))[0]
    raise ImageNotFound(f"No image found for sample {sample_name} in {dataset_root}")
