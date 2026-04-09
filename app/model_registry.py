from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ModelInfo:
    key: str
    label: str
    provider_id: str


class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, ModelInfo] = {
            # FINAL MODELS
            "claude-sonnet-4.5": ModelInfo(
                "claude-sonnet-4.5",
                "Claude Sonnet 4.5",
                "anthropic/claude-sonnet-4.5",
            ),
            "gemini-3-pro": ModelInfo(
                "gemini-3-pro",
                "Gemini 3 Pro",
                "google/gemini-3-pro-image-preview",
            ),
            "gpt-5.1": ModelInfo(
                "gpt-5.1",
                "GPT-5.1",
                "openai/gpt-5.1",
            ),
            "grok-4": ModelInfo(
                "grok-4",
                "Grok 4",
                "x-ai/grok-4",
            ),
        }

    def list_models(self) -> List[ModelInfo]:
        return list(self._models.values())

    def resolve(self, key: str) -> ModelInfo:
        if key not in self._models:
            raise ValueError(f"Unknown model key: {key}")
        return self._models[key]


model_registry = ModelRegistry()
