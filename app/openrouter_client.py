from __future__ import annotations

import asyncio
import json
import random
import re
import ssl
from typing import Any, Dict

import httpx

from .config import get_settings


class OpenRouterClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def complete(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.settings.openrouter_api_key:
            return self._mock_response(payload)

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": getattr(self.settings, "openrouter_http_referer", "http://localhost"),
            "X-Title": getattr(self.settings, "openrouter_app_title", "HQC-CAT"),
        }

        last_exc: Exception | None = None

        for attempt in range(1, 4):  # 3 attempts
            try:
                async with httpx.AsyncClient(
                    timeout=self.settings.request_timeout_seconds,
                    http2=False,
                    trust_env=True,
                ) as client:
                    response = await client.post(
                        self.settings.openrouter_base_url,
                        headers=headers,
                        json=payload,
                    )

                if response.status_code >= 400:
                    try:
                        body = response.json()
                    except Exception:
                        body = response.text
                    if isinstance(body, str):
                        body = body[:2000]
                    raise ValueError(f"OpenRouter HTTP {response.status_code} error: {body}")

                data = response.json()
                break  # success

            except (httpx.TransportError, ssl.SSLError) as exc:
                last_exc = exc
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

        else:
            raise ValueError(f"Network/TLS error talking to OpenRouter after retries: {last_exc}") from last_exc

        try:
            message = data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Unexpected OpenRouter response shape: {data}") from exc

        parsed = self._safe_json_from_message(message)
        if not isinstance(parsed, dict):
            raise ValueError("Model returned JSON but not an object (expected a JSON object).")
        return parsed

    def _safe_json_from_message(self, message: str) -> Any:
        if not isinstance(message, str):
            raise ValueError("Model message content is not a string.")

        text = message.strip()

        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except Exception:
            pass

        extracted = self._extract_first_json_block(text)
        if extracted is None:
            snippet = text[:500].replace("\n", "\\n")
            raise ValueError(f"Could not find JSON in model output. Snippet: {snippet}")

        try:
            return json.loads(extracted)
        except Exception as exc:  # noqa: BLE001
            snippet = extracted[:500].replace("\n", "\\n")
            raise ValueError(f"Found JSON-like block but failed to parse. Snippet: {snippet}") from exc

    def _extract_first_json_block(self, text: str) -> str | None:
        for i, ch in enumerate(text):
            if ch in "{[":
                start_idx, start_ch = i, ch
                break
        else:
            return None

        end_ch = "}" if start_ch == "{" else "]"
        depth = 0
        in_str = False
        esc = False

        for j in range(start_idx, len(text)):
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue

            if c == '"':
                in_str = True
                continue

            if c == start_ch:
                depth += 1
            elif c == end_ch:
                depth -= 1
                if depth == 0:
                    return text[start_idx : j + 1]

        return None

    def _mock_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = payload.get("model", "unknown")
        user_content = payload.get("messages", [{}])[1].get("content", [])
        sample_line = next(
            (
                part.get("text", "")
                for part in user_content
                if part.get("type") == "text" and part.get("text", "").startswith("sample_name")
            ),
            "sample_name: sample",
        )
        sample_name = sample_line.split(":", 1)[-1].strip() or "sample"

        def random_score(low: int = 6, high: int = 9) -> int:
            return random.randint(low, high)

        factors = [
            ("D1 – Factual Accuracy", 0.25),
            ("D1 – Completeness & Key Insights", 0.25),
            ("D1 – Context Alignment", 0.20),
            ("D2 – Conciseness & Brevity", 0.10),
            ("D2 – Language Quality & Tone", 0.10),
            ("D2 – Imaginability & Visual Detail", 0.10),
        ]

        evaluation_table = []
        for factor, weight in factors:
            evaluation_table.append(
                {
                    "factor": factor,
                    "weight": weight,
                    "score_1_to_10": random_score(),
                    "error_severity": "Minor",
                    "whats_wrong_missing_invented": "mock",
                    "l1_l4_coverage": {"L1": "ok", "L2": "ok", "L3": "ok", "L4": ""},
                }
            )

        return {
            "sample_name": sample_name,
            "model": model,
            "evaluation_table": evaluation_table,
        }


openrouter_client = OpenRouterClient()
