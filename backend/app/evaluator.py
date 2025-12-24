from __future__ import annotations

import json
from typing import Any, Dict

from .model_registry import model_registry
from .openrouter_client import openrouter_client
from .prompt_builder import build_messages
from .scoring import compute_scores, EvaluationValidationError


async def evaluate_sample(
    *,
    image_bytes: bytes,
    image_filename: str,
    sample_name: str,
    alt_text: str,
    caption: str | None,
    local_text: str | None,
    model_key: str,
) -> Dict[str, Any]:
    model_info = model_registry.resolve(model_key)
    payload = build_messages(
        image_bytes=image_bytes,
        image_filename=image_filename,
        alt_text=alt_text,
        caption=caption,
        local_text=local_text,
        sample_name=sample_name,
        model_provider_id=model_info.provider_id,
    )
    raw_response = await openrouter_client.complete(payload)
    if not isinstance(raw_response, dict):
        raise ValueError("Model response was not JSON.")
    try:
        evaluation_table = raw_response["evaluation_table"]
        final_score, _ = compute_scores(evaluation_table)
    except (KeyError, EvaluationValidationError) as exc:
        raise ValueError(f"Invalid evaluation table: {exc}") from exc

    return {
        "sample_name": raw_response.get("sample_name", sample_name),
        "model": raw_response.get("model", model_info.provider_id),
        "evaluation_table": evaluation_table,
        "improvement_report": raw_response.get("improvement_report", []),
        "final_score": final_score,
        "raw_response": raw_response,
        "model_key": model_key,
    }
