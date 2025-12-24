from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from .config import get_settings


@lru_cache(maxsize=1)
def load_hqcat_prompt() -> str:
    settings = get_settings()
    prompt_path = Path(settings.evaluator_prompt_path)
    return prompt_path.read_text(encoding="utf-8")


def _image_to_data_uri(image_bytes: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    mime = "image/png" if ext in {"png"} else "image/jpeg"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def build_messages(
    *,
    image_bytes: bytes,
    image_filename: str,
    alt_text: str,
    caption: Optional[str],
    local_text: Optional[str],
    sample_name: str,
    model_provider_id: str,
) -> Dict[str, Any]:
    system_prompt = load_hqcat_prompt()
    content_parts: list[Dict[str, Any]] = [
        {"type": "text", "text": f"sample_name: {sample_name}\nmodel: {model_provider_id}"},
        {"type": "text", "text": f"alt_text: {alt_text}"},
    ]
    if caption:
        content_parts.append({"type": "text", "text": f"caption: {caption}"})
    if local_text:
        content_parts.append({"type": "text", "text": f"local_text: {local_text}"})

    content_parts.append({"type": "image_url", "image_url": {"url": _image_to_data_uri(image_bytes, image_filename)}})

    return {
        "model": model_provider_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_parts},
        ],
        "response_format": {"type": "json_object"},
    }
