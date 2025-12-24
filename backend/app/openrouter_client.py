from __future__ import annotations

import json
import random
from typing import Any, Dict

import httpx

from .config import get_settings


class OpenRouterClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def complete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.settings.openrouter_api_key:
            # Offline deterministic fallback for development/testing
            return self._mock_response(payload)

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(
                self.settings.openrouter_base_url, headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            return json.loads(message)

    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = payload.get("model", "unknown")
        user_content = payload.get("messages", [{}])[1].get("content", [])
        alt_text_line = next(
            (part.get("text", "") for part in user_content if part.get("type") == "text" and part.get("text", "").startswith("alt_text")),
            "alt_text: (missing)",
        )
        alt_text_value = alt_text_line.split(":", 1)[-1].strip()
        sample_line = next(
            (part.get("text", "") for part in user_content if part.get("type") == "text" and part.get("text", "").startswith("sample_name")),
            "sample_name: sample",
        )
        sample_name = sample_line.split(":", 1)[-1].strip()

        def random_score() -> int:
            return random.randint(6, 9)

        evaluation_table = []
        factors = [
            ("D1 – Factual Accuracy", 0.25),
            ("D2 – Visual Encoding Fidelity", 0.15),
            ("D3 – Context and Purpose", 0.15),
            ("D4 – Comparative Reasoning", 0.15),
            ("D5 – Accessibility and Brevity", 0.15),
            ("D6 – Terminology and Conventions", 0.15),
        ]
        for idx, (factor, weight) in enumerate(factors):
            severity = "None" if idx != 0 else "Minor"
            evaluation_table.append(
                {
                    "factor": factor,
                    "weight": weight,
                    "score_1_to_10": random_score(),
                    "error_severity": severity,
                    "whats_wrong_missing_invented": f"Auto-evaluated placeholder for {factor}",
                    "l1_l4_coverage": {
                        "L1": "Stub L1",
                        "L2": "Stub L2",
                        "L3": "Stub L3",
                        "L4": "Stub L4",
                    },
                }
            )

        return {
            "sample_name": sample_name,
            "model": model,
            "evaluation_table": evaluation_table,
            "improvement_report": [
                f"Clarify details for {alt_text_value[:20] or 'alt text'}.",
                "State axes and units explicitly.",
                "Summarize the main comparison succinctly.",
            ],
        }


openrouter_client = OpenRouterClient()
